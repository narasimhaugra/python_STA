import os
import threading

import cv2
import simple_colors

exitFlag = False


# def videoRecord(name, videoPath):
#     try:
#         frame_rate = 30
#         video = cv2.VideoCapture(1 + cv2.CAP_DSHOW)
#         cod = cv2.VideoWriter.fourcc(*'mp4v')
#         os.chdir(videoPath)
#         out = cv2.VideoWriter(name + '.mp4', cod, frame_rate, (640, 480))
#
#         a = 0
#         b = 0
#         while True:
#             a += 1
#             check, frame = video.read()
#
#             cv2.imshow('capturing', frame)
#             out.write(frame)
#             key = cv2.waitKey(1)
#
#             if exitFlag == True:
#                 break
#         # print(a)
#         video.release()
#         out.release()
#         cv2.destroyAllWindows()
#         print(f"video has been saved successfully in the {videoPath} directory !")
#     except Exception as ex:
#         print(f"Exception encountered while capturing the video! {ex}")


class myThread(threading.Thread):
    def __init__(self, name, videoPath):
        threading.Thread.__init__(self)
        self.name = name
        self.videoPath = videoPath
        # print("name, path ", self.name, self.videoPath)
        self.folder_name = None
        self.image_file_name = None
        self.__capture_images = False
        self.__is_static_image = True

    def __videoRecord(self):
        try:
            frame_rate = 30
            video = cv2.VideoCapture(1 + cv2.CAP_DSHOW)
            cod = cv2.VideoWriter.fourcc(*'mp4v')
            os.chdir(self.videoPath)
            out = cv2.VideoWriter(self.name + '.mp4', cod, frame_rate, (640, 480))

            cnt = 0
            frame_count = 0
            while True:
                check, frame = video.read()
                # print("check and  frmae", check, frame)
                cv2.imshow('capturing', frame)
                if self.__capture_images:
                    cnt += 1
                    if self.folder_name is not None:
                        output_dir = f'{self.videoPath}/Images/{self.folder_name}'
                        if not os.path.exists(output_dir):
                            try:
                                os.makedirs(output_dir)
                            except FileExistsError:
                                print(f"Directory '{output_dir}' already exists.")
                            except PermissionError:
                                print(f"Permission denied: Unable to create '{output_dir}'.")
                            except Exception as e:
                                print(f"An error occurred: {e}")
                        if not self.__is_static_image and (cnt % 6) != 0:
                            continue
                        frame_count += 1
                        file_name = f'{output_dir}/{frame_count}.png'
                        if self.image_file_name is not None:
                            file_name = f'{output_dir}/{self.image_file_name}_{frame_count}.png'

                        is_written = cv2.imwrite(filename=file_name, img=frame)
                        if is_written:
                            print(simple_colors.green(f'{file_name} is written successfully !'))
                        if self.__is_static_image and cnt >= 5:
                            self.set_capture_images(False)
                else:
                    cnt = 0
                    frame_count = 0
                out.write(frame)
                key = cv2.waitKey(1)

                if exitFlag:
                    break
            # print(a)
            video.release()
            out.release()
            cv2.destroyAllWindows()
            print(f"video has been saved successfully in the {self.videoPath} directory !")
        except Exception as ex:
            print(f"Exception encountered while capturing the video! {ex}")

    def set_capture_images(self, capture_images:bool):
        self.__capture_images = capture_images
        if not capture_images:
            self.folder_name = None
            self.image_file_name = None
            self.__is_static_image = True

    def set_is_static_image(self, is_static_image:bool):
        self.__is_static_image = is_static_image

    def run(self):
        print("Starting video: " + self.name)
        global exitFlag
        exitFlag = False
        self.__videoRecord()

    def stop_recording(self):
        print("Stopping and saving the video: " + self.name)
        global exitFlag
        exitFlag = True