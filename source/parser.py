import pykitti
import numpy as np
from scipy import ndimage as nd
from collections import namedtuple
import cv2

class DataParser():
    def __init__(self, basedir, date, drive):
        # Load the data. Optionally, specify the frame range to load.
        self.dataset = pykitti.raw(basedir, date, drive)
        # dataset = pykitti.raw(basedir, date, drive, frames=range(0, 20, 5))

        # Display some of the data
        np.set_printoptions(precision=4, suppress=True)
        print('\nDrive: ' + str(self.dataset.drive))
        print('\nFrame range: ' + str(self.dataset.frames))
        print('\nIMU-to-Velodyne transformation:\n' + str(self.dataset.calib.T_velo_imu))
        print('\nGray stereo pair baseline [m]: ' + str(self.dataset.calib.b_gray))
        print('\nRGB stereo pair baseline [m]: ' + str(self.dataset.calib.b_rgb))
        self._load_data()

    def _load_data(self):
        storage = {}
        storage["focal_pix_RGB"] = self.dataset.calib.K_cam2[0][0]
        storage["baseline_m_RGB"] = self.dataset.calib.b_rgb
        # storage["project_mtx"] = self.dataset.calib.P_rect_20
        self.storage = namedtuple("storage", storage.keys())(*storage.values())

    def get_ground_truth(self, image_idx):
        velo_points = self.dataset.get_velo(image_idx)
        idx = np.where(velo_points[:,0]>5)[0]
        velo_points = velo_points[idx, :]
        velo_points = velo_points[:,0:3]

        P_rect = self.dataset.calib.P_rect_20
        R_cam_to_rect = self.dataset.calib.R_rect_00 # for all cameras
        Tr_velo_to_cam = self.dataset.calib.T_cam0_velo_unrect # for all cameras

        P_velo_to_img = P_rect.dot(R_cam_to_rect).dot(Tr_velo_to_cam)

        velo_img = DataParser.project(velo_points, P_velo_to_img)
        velo_img = np.around(velo_img)
        velo_depth = velo_points[:,0]

        dim_y, dim_x = np.array(self.dataset.get_cam2(image_idx)).shape[0:2]
        depth_map = np.full((dim_y, dim_x), np.nan)

        velo_y_min = np.inf
        for iter_, (xx, yy) in enumerate(velo_img):
            if xx >= 0  and xx <= dim_x-1 and yy >= 0 and yy <= dim_y-1 and velo_depth[iter_] >= 0:
                depth_map[int(yy), int(xx)] = velo_depth[iter_]
                if velo_y_min > yy:
                    velo_y_min = yy

        depth_map[:int(velo_y_min), :] = -1
        return DataParser.fill(depth_map)


    def get_stereo_map(self, image_idx):
        left_RGB = self.get_left_RGB(image_idx) # left RGB image
        right_RGB = self.get_right_RGB(image_idx) # right RGB image
        # compute depth map from stereo
        stereo = cv2.StereoBM_create()
        stereo.setMinDisparity(0)
        num_disparities = 16*5
        stereo.setNumDisparities(num_disparities)
        stereo.setBlockSize(15)
        stereo.setSpeckleRange(16)
        # stereo.setSpeckleWindowSize(45)
        stereo_depth_map = stereo.compute(
            cv2.cvtColor(np.array(left_RGB), cv2.COLOR_RGB2GRAY),
            cv2.cvtColor(np.array(right_RGB), cv2.COLOR_RGB2GRAY))
        # by equation + divide by 16 to get true disperities
        stereo_depth_map = (self.storage.focal_pix_RGB * self.storage.baseline_m_RGB) \
                            / (stereo_depth_map/16)
        stereo_depth_map = DataParser.crop_redundant(stereo_depth_map)
        return stereo_depth_map


    def get_velocity(self, image_idx):
        """Velocity in meters"""
        return self.dataset.oxts[image_idx][0].vf


    def get_left_RGB(self, image_idx):
        return self.dataset.get_cam2(image_idx) # left RGB image


    def get_right_RGB(self, image_idx):
        return self.dataset.get_cam3(image_idx) # right RGB image


    def __len__(self):
        return len(self.dataset.cam2_files)


    @staticmethod
    def crop_redundant(stereo_depth_map):
        left_crop_idx = 0
        img_width = stereo_depth_map.shape[1]
        right_crop_idx = img_width - 1
        for idx in range(int(img_width/2)):
            list_left = stereo_depth_map[:,idx]
            list_right = stereo_depth_map[:, img_width -1 -idx]
            if np.all(list_left<0):
                left_crop_idx = idx
            if np.all(list_right<0):
                right_crop_idx = img_width -1 -idx

        stereo_depth_map[stereo_depth_map<0] = -1
        # stereo_depth_map[stereo_depth_map<0] = np.nan
        stereo_depth_map = DataParser.fill(stereo_depth_map)
        stereo_depth_map[stereo_depth_map>50] = 30
        stereo_depth_map[:, :left_crop_idx] = -1
        stereo_depth_map[:, right_crop_idx:] = -1
        stereo_depth_map[:120,:] = -1
        return stereo_depth_map


    @staticmethod
    def project(velo_points, P_velo_to_img):
        # dimension of data and projection matrix
        dim_norm = P_velo_to_img.shape[0]
        dim_proj = P_velo_to_img.shape[1]

        p2_in = velo_points
        if velo_points.shape[1] < dim_proj:
            ones_arr = np.ones((velo_points.shape[0],1), dtype=np.float32)
            p2_in = np.append(velo_points, ones_arr, axis=1)

        p2_out = np.transpose(P_velo_to_img.dot(np.transpose(p2_in)))
        pass
        # normalize homogeneous coordinates:
        p_out = p2_out[:,0:dim_norm-1] / np.outer(p2_out[:,dim_norm-1, None], np.ones(dim_norm-1))
        return p_out


    @staticmethod
    def fill(data, invalid=None):
        if invalid is None: invalid = np.isnan(data)
        ind = nd.distance_transform_edt(invalid,
                                        return_distances=False,
                                        return_indices=True)
        return data[tuple(ind)]
