import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast
import config
from dataset import get_dataloaders
from model_arch import build_model, unfreeze_last_block

def run_epoch(model, loader, criterion, optimizer=None, scaler=None):
    is_train = optimizer is not None
    model.train() if is_train else model.eval()

    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(is_train):
        for images, labels in loader:
            images, labels = images.to(config.DEVICE), labels.to(config.DEVICE)

            if is_train:
                optimizer.zero_grad()
                with autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                with autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

    return total_loss / total, correct / total


def train_phase(model, train_loader, val_loader, criterion, optimizer, scaler, epochs, phase_name, best_val_acc):
    print(f"\n--- {phase_name} ---")
    for epoch in range(epochs):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, scaler)
        val_loss, val_acc = run_epoch(model, val_loader, criterion)
        print(f"Epoch {epoch} | train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), config.BEST_MODEL_PATH)
    return best_val_acc


def main():
    print(config.DEVICE)
    train_loader, val_loader, test_loader, class_names = get_dataloaders()
    print(class_names)

    model = build_model()
    criterion = nn.CrossEntropyLoss()
    scaler = GradScaler()
    best_val_acc = 0.0

    optimizer = torch.optim.Adam(model.fc.parameters(), lr=config.HEAD_LR)
    best_val_acc = train_phase(model, train_loader, val_loader, criterion, optimizer, scaler,
                                config.HEAD_EPOCHS, best_val_acc)

    unfreeze_last_block(model)
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=config.FINETUNE_LR)
    best_val_acc = train_phase(model, train_loader, val_loader, criterion, optimizer, scaler,
                                config.FINETUNE_EPOCHS, best_val_acc)

    print(f"{best_val_acc:.4f}")

if __name__ == "__main__":
    main()