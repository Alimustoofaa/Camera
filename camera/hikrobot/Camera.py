from .Config import *
from .MvCameraControl_class import *

class HikRobotCamera:
	def __init__(self, ip: str):
		self.nConnectionNum = None
		self.ip	= ip
		self.deviceList = list()
		self.startup(); self.__devices_list()
		pass
	
	def startup(self):
		SDKVersion = MvCamera.MV_CC_GetSDKVersion()
		print ("SDKVersion[0x%x]" % SDKVersion)
		deviceList = MV_CC_DEVICE_INFO_LIST()
		self.deviceList = deviceList
		tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
  
		# ch:枚举设备 | en:Enum device
		ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
		if ret != 0:
			print ("enum devices fail! ret[0x%x]" % ret)
			sys.exit()

		if deviceList.nDeviceNum == 0:
			print ("find no device!")
			sys.exit()
		print ("Find %d devices!" % deviceList.nDeviceNum)
  
	def __devices_list(self):
		for i in range(0, self.deviceList.nDeviceNum):
			mvcc_dev_info = cast(self.deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
			if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
				print ("\ngige device: [%d]" % i)
				strModeName = ""
				for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
					strModeName = strModeName + chr(per)
				print ("device model name: %s" % strModeName)

				nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
				nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
				nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
				nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
				ip_device = f'{nip1}.{nip2}.{nip3}.{nip4}'
				if self.ip == ip_device:
					print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
					self.nConnectionNum = i
			elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
				print ("\nu3v device: [%d]" % i)
				strModeName = ""
				for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
					if per == 0:
						break
					strModeName = strModeName + chr(per)
				print ("device model name: %s" % strModeName)

				strSerialNumber = ""
				for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
					if per == 0:
						break
					strSerialNumber = strSerialNumber + chr(per)
				print ("user serial number: %s" % strSerialNumber)
   
	def config_params(self, cam):
	   # Set trigger mode as off
		ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
		if ret != 0:
			print ("set trigger mode fail! ret[0x%x]" % ret)
			sys.exit()

		ret = cam.MV_CC_SetFloatValue('ExposureTime', EXPOSURE_TIME)
		if ret != 0:
			print ("set ExposureTime mode fail! ret[0x%x]" % ret)
			sys.exit()
		return cam

	def close_camera(self, cam, data_buf):
		#Stop grab image
		ret = cam.MV_CC_StopGrabbing()
		if ret != 0:
			print ("stop grabbing fail! ret[0x%x]" % ret)
			del data_buf
			sys.exit()
		#Close device
		ret = cam.MV_CC_CloseDevice()
		if ret != 0:
			print ("close deivce fail! ret[0x%x]" % ret)
			del data_buf
			sys.exit()

		# ch:销毁句柄 | Destroy handle
		ret = cam.MV_CC_DestroyHandle()
		if ret != 0:
			print ("destroy handle fail! ret[0x%x]" % ret)
			del data_buf
			sys.exit()

		del data_buf
		
	def open_camera(self):
		if self.nConnectionNum == None:
			print (f'Device {self.nConnectionNum}, Ip {self.ip} Not Connected')
			sys.exit()
		if int(self.nConnectionNum) >= self.deviceList.nDeviceNum:
			print (f'Device {self.nConnectionNum}, Ip {self.ip} Not Connected')
			sys.exit()

		# Create camera object
		cam = MvCamera()
		# Select device and create handle
		stDeviceList = cast(
							self.deviceList.pDeviceInfo[int(self.nConnectionNum)], 
							POINTER(MV_CC_DEVICE_INFO)
						).contents
		ret = cam.MV_CC_CreateHandle(stDeviceList)
		if ret != 0:
			print ("create handle fail! ret[0x%x]" % ret)
			sys.exit()
   
		# Open device
		ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
		if ret != 0:
			print ("open device fail! ret[0x%x]" % ret)
			sys.exit()
   
		# Detection network optimal package size(It only works for the GigE camera)
		if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
			nPacketSize = cam.MV_CC_GetOptimalPacketSize()
			if int(nPacketSize) > 0:
				ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
				if ret != 0:
					print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
			else:
				print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)
		'''
		CONFIGURATION CAMERA PARAM
  		'''
		#cam = self.config_params(cam)
  
		# Get payload size
		stParam =  MVCC_INTVALUE()
		memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

		ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
		if ret != 0:
			print ("get payload size fail! ret[0x%x]" % ret)
			sys.exit()
		nPayloadSize = stParam.nCurValue

		# Start grab image
		ret = cam.MV_CC_StartGrabbing()
		if ret != 0:
			print ("start grabbing fail! ret[0x%x]" % ret)
			sys.exit()

		data_buf = (c_ubyte * nPayloadSize)()
		return cam, data_buf, nPayloadSize


  


  