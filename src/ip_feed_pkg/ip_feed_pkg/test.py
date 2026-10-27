import cv2

rtsp_url = "rtsp://admin:aurora123@192.168.1.200:554/cam/realmonitor?channel=1&subtype=0"

cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream")
    exit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    cv2.imshow("RTSP Stream", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()