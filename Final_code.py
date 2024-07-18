import threading
import cv2
import imutils
import smtplib
import supervision as sv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from ultralytics import YOLO
import requests
class VideoCapture:
 def _init_(self, name):
 self.cap = cv2.VideoCapture(name)
 def read(self):
 return self.cap.read()
URL = "" #paste the url here
cap = VideoCapture(URL + ":81/stream")
# Size of the output camera (adjust if needed)
cap.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# Initializing the 1st frame with which we want to differentiate the current 
frame
_, start_frame = cap.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)
# Setting alarm
alarm = False
alarm_mode = False
alarm_counter = 0
# Email configuration (replace with your credentials)
password = "your_password"
sender_email = "your_email@gmail.com"
receiver_email = "recipient_email@gmail.com"
# Function to send email notification
def send_email(subject, body):
 message = MIMEMultipart()
 message["From"] = sender_email
 message["To"] = receiver_email
 message["Subject"] = subject
 message.attach(MIMEText(body, "plain"))
 try:
 server = smtplib.SMTP("smtp.gmail.com:587")
 server.ehlo()
 server.starttls()
 server.login(sender_email, password)
 server.sendmail(sender_email, receiver_email, message.as_string())
 server.quit()
 print(f"Email sent: {subject}")
 except Exception as e:
 print(f"Error sending email: {e}")
# Object detection model (replace with your model path)
model = YOLO("yolov8s.pt")
bbox_annotator = sv.BoxAnnotator()
# Function to send email notification
def beep_alarm(object_name):
 global alarm
 current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 email_body = (
 f"Motion detected with object identified: {object_name} at 
{current_time}"
 )
 send_email("Motion Alert - Object Detected", email_body)
 alarm = False
if _name_ == '_main_':
 requests.get(URL + "/control?var=framesize&val={}".format(8))
while True:
 ret, frame = cap.read()
 if ret:
 frame = imutils.resize(frame, width=500)
 if alarm_mode:
 frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)
 difference = cv2.absdiff(frame_bw, start_frame)
 threshold = cv2.threshold(difference, 25, 255, 
cv2.THRESH_BINARY)[1]
 start_frame = frame_bw
 if threshold.sum() > 400000:
 alarm_counter += 1
 else:
 if alarm_counter > 0:
 alarm_counter -= 1
 cv2.imshow("cam", threshold)
 else:
 cv2.imshow("cam", frame)
 if alarm_counter > 20:
 if not alarm:
 alarm = True
 result = model(frame)[0]
 detections = sv.Detections.from_ultralytics(result)
 detections = detections[detections.confidence > 0.5]
 if detections:
 labels = [
 result.names[class_id] for class_id in detections.class_id
 ]
 for object_name in labels:
 threading.Thread(target=beep_alarm, 
args=(object_name,)).start()
 key_pressed = cv2.waitKey(30)
 if key_pressed == ord("t"):
 alarm_mode = not alarm_mode
 alarm_counter = 0
 if key_pressed == ord("q"):
 alarm_mode = False
 break
 cv2.imshow("gray_frame", start_frame)
cv2.destroyAllWindows()
