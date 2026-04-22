"""
Full diagnostic - saves annotated frames to disk to verify detection
Run from parking_monitor directory: python diagnose.py
"""
import cv2
from ultralytics import YOLO
import os

model = YOLO('yolov8n.pt')

for video_name in ['parking_video.mp4', 'parking_cctv.mp4', 'parking_3.mp4']:
    if not os.path.exists(video_name):
        print(f"SKIP {video_name} - file not found")
        continue

    cap = cv2.VideoCapture(video_name)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"\n=== {video_name}: {width}x{height}, {total_frames} frames ===")

    # Try frames at 5%, 25%, 50%, 75%
    for pct in [5, 25, 50, 75]:
        idx = int(total_frames * pct / 100)
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"  Frame {idx} ({pct}%): UNREADABLE")
            continue

        # Run YOLO without class filter first - detect EVERYTHING
        results_all = model.predict(frame, verbose=False, conf=0.25)
        all_labels = [model.names[int(c)] for c in results_all[0].boxes.cls.cpu().numpy()] if len(results_all[0].boxes) else []

        # Now with car/truck/bus filter
        results = model.predict(frame, classes=[2, 5, 7], verbose=False, conf=0.25)
        n_cars = len(results[0].boxes)

        print(f"  Frame {idx} ({pct}%): {n_cars} vehicles | all detections: {all_labels}")

        # Save annotated frame
        out = results[0].plot()
        fname = f"diag_{video_name.replace('.mp4','')}_{pct}.jpg"
        cv2.imwrite(fname, out)
        print(f"    → saved {fname}")

    cap.release()

print("\nDone. Open the diag_*.jpg files to see what YOLO actually detects.")
