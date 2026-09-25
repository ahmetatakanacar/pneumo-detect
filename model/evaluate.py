import torch
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
import config
from dataset import get_dataloaders
from model_arch import build_model


def evaluate(model, loader):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(config.DEVICE)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)[:, 1]
            all_preds.extend(outputs.argmax(dim=1).cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())

    metrics = {
        "precision": precision_score(all_labels, all_preds),
        "recall": recall_score(all_labels, all_preds),
        "f1": f1_score(all_labels, all_preds),
        "auc": roc_auc_score(all_labels, all_probs),
    }
    print(f"Precision: {metrics['precision']:.4f}  Recall: {metrics['recall']:.4f}  "
          f"F1: {metrics['f1']:.4f}  AUC-ROC: {metrics['auc']:.4f}")
    return metrics


def main():
    _, _, test_loader, class_names = get_dataloaders()
    print(class_names)

    model = build_model()
    model.load_state_dict(torch.load(config.BEST_MODEL_PATH, map_location=config.DEVICE))

    evaluate(model, test_loader)


if __name__ == "__main__":
    main()