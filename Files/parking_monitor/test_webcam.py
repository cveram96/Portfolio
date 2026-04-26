"""
Simple script to test webcam without GUI.
Run from console: python test_webcam.py
"""
import cv2
import sys

def test_webcam(idx=0):
    print(f"Testing webcam {idx}...")
    
    # Try with DirectShow backend (Windows)
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"DirectShow failed, trying without backend...")
        cap = cv2.VideoCapture(idx)
    
    if not cap.isOpened():
        print(f"ERROR: Could not open webcam {idx}")
        return False
    
    print(f"Webcam {idx} opened successfully")
    print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    print(f"Frame size: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    
    # Read and display a few frames
    for i in range(30):
        ret, frame = cap.read()
        if not ret:
            print(f"ERROR: Failed to read frame {i}")
            break
        
        print(f"Frame {i}: {frame.shape}")
        cv2.imshow(f'Webcam {idx}', frame)
        
        # Press 'q' to quit, or wait 100ms
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Test completed!")
    return True

if __name__ == "__main__":
    idx = 0
    if len(sys.argv) > 1:
        idx = int(sys.argv[1])
    test_webcam(idx)
