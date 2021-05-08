import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, Float
import pandas as pd
from database import Image as ImageModel, Mask as MaskModel, Video as VideoModel
import cv2
from PIL import Image
from object_movement import Object_Tracker
import base64
from datetime import datetime
from tracking import trackObject
import tempfile

# connect to database
engine = create_engine("sqlite:///db.sqlite3?check_same_thread=False")
Session = sessionmaker(bind=engine)
sess = Session()

st.title("Camera Based Object Tracking System")

sidebar = st.sidebar
sidebar.header("Choose an option")


def addImage():
    st.header("Upload image to continue")
    img_name = st.text_input("Enter image name")

    img_file = st.file_uploader("Insert Image Here")

    if img_file:
        
        img = Image.open(img_file)
        st.image(img)
        img_path = "./uploads/" + img_name + ".png"
        img.save(img_path)

    add_btn = st.button("Save image")

    if add_btn and img_name and img_file:
        with st.spinner("Saving your Image"):
            img_data = ImageModel(name=img_name, path=img_path)
            sess.add(img_data)
            sess.commit()
            st.success("Image successfully saved")

def addVideo():
    vid_name = st.text_input("Enter video name")
    f = st.file_uploader("Upload video file")
    video_thumb = st.image([])
    if f:
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(f.read())
        st.video(tfile.name)
        btn = st.button("Submit")
        if btn:
            with st.spinner("Saving your Video ..."):
                try:
                    cap = cv2.VideoCapture(tfile.name)
                    ret, frame = cap.read()
                    num = 0
                    shape = frame.shape

                    codec = cv2.VideoWriter_fourcc(*'XVID')
                    vid_path = 'uploads/'+vid_name+'.mp4'
                    out = cv2.VideoWriter(vid_path, codec, 30.0, (shape[1],shape[0]))
                    while(cap.isOpened()):
                        if ret==True:
                            out.write(frame) 
                        else:
                            break
                        ret, frame = cap.read()
                    cap.release()
                    out.release()
                    cv2.destroyAllWindows()

                    video = VideoModel(
                        name=vid_name,
                        path=vid_path,
                    )
                    sess.add(video)
                    sess.commit()

                    st.success("Video Saved Successfully")
                except Exception as e:
                    st.error('Something went wrong')
                    print(e)


def showMask(selObj, FRAME_WINDOW):
    st.markdown("### Adjust Sliders to create a mask for Tracking")
    sliders = setupsliders()
    mask_name = st.text_input("Enter name for masked image")
    save_btn = st.button("Save Mask Image")
    range_filter = "HSV"

    if selObj.path:
        image = cv2.imread(selObj.path)
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        camera = cv2.VideoCapture(0)

    while True:

        # v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
        thresh = cv2.inRange(
            frame_to_thresh,
            (sliders["v1_min"], sliders["v2_min"], sliders["v3_min"]),
            (sliders["v1_max"], sliders["v2_max"], sliders["v3_max"]),
        )

        if save_btn:
            try:
                mask_filename = "masks/masked_" + selObj.name + ".jpg"
                cv2.imwrite(mask_filename, thresh)
                print(sliders)
                mask_values = ",".join([str(value) for value in sliders.values()])
                mask = MaskModel(
                    filename=mask_name,
                    mask_filename=mask_filename,
                    mask_values=mask_values,
                    created=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                )
                sess.add(mask)
                sess.commit()
                st.success("Masked Image Saved successfully")
                return None
            except Exception as e:
                st.error("error occured in saving mask image")
                print(e)

        FRAME_WINDOW.image(thresh)


def trackObj():
    st.header("Live Object Tracking")
    run = st.checkbox("Run")
    FRAME_WINDOW = st.image([])
    camera = cv2.VideoCapture(0)

    frameobj = Object_Tracker((0, 79, 144, 255, 222, 255))
    frameobj.track_object()


def showsavedImg():
    st.markdown("## Create Masked Image")
    saved_img = sess.query(ImageModel).all()
    image_names = [image.name for image in saved_img]
    sel_image_name = st.selectbox(options=image_names, label="Select Image to Mask")
    col1, col2 = st.beta_columns(2)
    org_image = col1.image([])
    masked_image = col2.image([])
    btn = st.checkbox("Use This Image to create Mask")

    selObj = sess.query(ImageModel).filter_by(name=sel_image_name).first()
    org_image.image(selObj.path)

    if btn:
        showMask(selObj, masked_image)


def showSavedMasks():
    st.markdown("## Live Object Movement Tracking with WebCam")
    saved_img = sess.query(MaskModel).all()
    image_names = [image.filename for image in saved_img]
    sel_image_name = st.selectbox(options=image_names, label="Select Mask to track")
    org_image = st.image([])
    btn = st.checkbox("Start Tracking")

    selObj = sess.query(MaskModel).filter_by(filename=sel_image_name).first()
    org_image.image(selObj.mask_filename)
    mask_values = tuple([int(value) for value in selObj.mask_values.split(",")])

    if btn:
        trackObject(mask_values[:3], mask_values[3:])


def showSavedVideos():
    st.markdown("## Live Object Movement Tracking with Video")
    saved_img = sess.query(MaskModel).all()
    image_names = [image.filename for image in saved_img]

    saved_vids = sess.query(VideoModel).all()
    print(saved_vids)
    video_names = [video.name for video in saved_vids]

    col1, col2 = st.beta_columns(2)

    sel_image_name = col1.selectbox(options=image_names, label="Select Mask to track")
    org_image = col1.image([])

    sel_video_name = col2.selectbox(options=video_names, label="Select Video to track")

    btn = st.checkbox("Start Tracking")

    selObj = sess.query(MaskModel).filter_by(filename=sel_image_name).first()

    selVideoObj = sess.query(VideoModel).filter_by(name=sel_video_name).first()
    col2.video(selVideoObj.path)
    print(selVideoObj.path)

    org_image.image(selObj.mask_filename)
    mask_values = tuple([int(value) for value in selObj.mask_values.split(",")])

    if btn:
        trackObject(mask_values[:3], mask_values[3:], selVideoObj.path)

def setupsliders():
    values = ["v1_min", "v2_min", "v3_min", "v1_max", "v2_max", "v3_max"]
    cap_values = {}
    set1, set2 = st.beta_columns(2)
    for index, value in enumerate(values):
        if index < 3:
            cap_values[value] = set1.slider(value, 0, 255)
        else:
            cap_values[value] = set2.slider(value, 0, 255, 255)

    return cap_values

options = ["Add image for masking", "Upload Video", "Create masked image", "Track Object with Video", "Track Object with webcam"]
choice = sidebar.selectbox(options=options, label="Choose any option")

if choice == options[0]:
    addImage()
elif choice == options[1]:
    addVideo()
elif choice == options[2]:
    showsavedImg()
elif choice == options[3]:
    showSavedVideos()
elif choice == options[4]:
    showSavedMasks()