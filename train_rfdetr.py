import os
import time
from datetime import datetime, timedelta
from rfdetr import RFDETRMedium

# Initialize model (medium backbone version of RF-DETR)
model = RFDETRMedium()

# Training parameters
dataset_dir = r"data\merged_dataset"
epochs = 50
batch_size = 4
grad_accum_steps = 4
lr = 1e-4
output_dir = r"./output_rfdetr_merge_dataset"

# Make sure output dir exists
os.makedirs(output_dir, exist_ok=True)

# Log file path
log_file = os.path.join(output_dir, "training_log.txt")

# Open log file
with open(log_file, "a") as log:
    log.write(f"\n=== Training started at {datetime.now()} ===\n")
    log.write(f"Dataset: {dataset_dir}\n")
    log.write(f"Epochs: {epochs}, Batch size: {batch_size}, Grad Accum Steps: {grad_accum_steps}, LR: {lr}\n")

start_time = time.time()

# Start training
for epoch in range(epochs):
    epoch_start = time.time()

    # Train for 1 epoch
    model.train(
        dataset_dir=dataset_dir,
        epochs=1,   # train one epoch at a time
        batch_size=batch_size,
        grad_accum_steps=grad_accum_steps,
        lr=lr,
        output_dir=output_dir
    )

    epoch_time = time.time() - epoch_start
    elapsed = time.time() - start_time
    avg_time_per_epoch = elapsed / (epoch + 1)
    remaining_time = avg_time_per_epoch * (epochs - epoch - 1)
    expected_finish = datetime.now() + timedelta(seconds=remaining_time)

    log_message = (
        f"Epoch {epoch+1}/{epochs} completed in {epoch_time:.2f}s\n"
        f"Elapsed: {elapsed/60:.2f} min, Remaining: {remaining_time/60:.2f} min\n"
        f"Expected finish time: {expected_finish.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    print(log_message)  # also print to terminal
    with open(log_file, "a") as log:
        log.write(log_message)

# Final log
with open(log_file, "a") as log:
    log.write(f"=== Training finished at {datetime.now()} ===\n")
