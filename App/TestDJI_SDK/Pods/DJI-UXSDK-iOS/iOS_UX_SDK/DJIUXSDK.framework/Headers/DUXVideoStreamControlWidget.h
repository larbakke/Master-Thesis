//
//  DUXVideoStreamControlWidget.h
//  DJIUXSDK
//
//  MIT License
//  
//  Copyright © 2020 DJI
//

#import <DJIUXSDK/DJIUXSDK.h>


/**
 *  Display:
 *  Widget for switch live stream source. Only supported on H20/H20T/H20N.
 *
 *  Usage:
 *  Preferred Aspect Ration: 80:120
 */
@interface DUXVideoStreamControlWidget : DUXWidget


/**
 *  `YES` if widget is supported, `NO` otherwise.
 *  Only supported on H20/H20T/H20N..
 */
@property (readonly) BOOL isSupported;


/**
 *  The index representing the camera that the widget controls. Default is 0.
 */
@property (nonatomic) NSUInteger preferredCameraIndex;


/**
 *  Display:
 *  Current video stream source that the camera is in.
 */
@property DJICameraVideoStreamSource videoStreamSource;

@end

