import cv2
import webbrowser
import time
import numpy as np
import subprocess

def open_url(url):
    webbrowser.open(url)

def close_last_tab():
    # This works for Chrome on Mac. Adjust if using a different browser or OS.
    apple_script = '''
    tell application "Google Chrome"
        close active tab of front window
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script])

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    qr_detector = cv2.QRCodeDetector()

    last_url = None
    last_open_time = 0
    frame_count = 0
    qr_codes_detected = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        if frame_count % 5 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(gray)

            if detected:
                qr_codes_detected = sum(1 for info in decoded_info if info)
                for info, point_set in zip(decoded_info, points):
                    if info:
                        points = np.int32(point_set).reshape(-1, 2)
                        cv2.polylines(frame, [points], True, (0, 255, 0), 2)
                        label = f"QR Code: {info[:20]}..."
                        cv2.putText(frame, label, (points[0][0], points[0][1] - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        if info.startswith(('http://', 'https://')):
                            current_time = time.time()
                            if qr_codes_detected > 1 or (info != last_url and current_time - last_open_time > 5):
                                if last_url:
                                    close_last_tab()
                                print(f"Opening URL: {info}")
                                open_url(info)
                                last_url = info
                                last_open_time = current_time
            else:
                qr_codes_detected = 0

        cv2.imshow('Mac Camera', frame)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()