import numpy as np
import face_recognition

def faceRecog(Known_Face_Encoding ,image_np):
    
    row,col,plane = image_np.shape
    x, y = 4, 4

    blue_plane = image_np[:,:,0]
    green_plane = image_np[:,:,1]
    red_plane = image_np[:,:,2]

    resize_blue_plane = blue_plane[1::x,1::x]
    resize_green_plane = green_plane[1::x,1::x]
    resize_red_plane = red_plane[1::x,1::x]
    
    newRow, newCol = resize_blue_plane.shape
    small_frame = np.zeros((newRow, newCol, 3),np.uint8)

    small_frame[:,:,0] = resize_blue_plane
    small_frame[:,:,1] = resize_green_plane
    small_frame[:,:,2] = resize_red_plane
    

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(small_frame)

    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    name = "False"

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces([Known_Face_Encoding], face_encoding)
        print(matches)
        face_distances = face_recognition.face_distance([Known_Face_Encoding], face_encoding)
        print(face_distances)
        if (matches[0] and  face_distances[0] < 0.50):
            name = "True"
    return name
