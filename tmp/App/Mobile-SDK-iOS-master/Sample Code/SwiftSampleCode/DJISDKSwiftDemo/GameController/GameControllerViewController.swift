//
//  GameControllerViewController.swift
//  DJISDKSwiftDemo
//
//  Created by Dennis Baldwin on 8/23/20.
//  Copyright © 2020 DJI. All rights reserved.
//

import UIKit
import GameplayKit
import GameController

class GameControllerViewController: UIViewController {
    
    private var flightController: DJIFlightController?
    
    private var roll: Float = 0
    private var pitch: Float = 0
    private var yaw: Float = 0
    private var throttle: Float = 0
    
    @IBOutlet weak var fpvView: UIView!
    var adapter: VideoPreviewerAdapter?
    
    // Handles sending commands to flight controller
    var timer: Timer?
    
    //
    var takeOffInProgress = false
    var landInProgress = false

    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Grab a reference to the aircraft
        if let aircraft = DJISDKManager.product() as? DJIAircraft {

            // Grab a reference to the flight controller
            if let fc = aircraft.flightController {
                // Store the flightController
                self.flightController = fc
                
                // Default the coordinate system to ground
                fc.rollPitchCoordinateSystem = DJIVirtualStickFlightCoordinateSystem.body

                // Default roll/pitch control mode to velocity
                fc.rollPitchControlMode = DJIVirtualStickRollPitchControlMode.velocity

                // Set control modes
                fc.yawControlMode = DJIVirtualStickYawControlMode.angularVelocity
                
            }
            
            // Setup the video preview
            DJIVideoPreviewer.instance()?.start()
            adapter = VideoPreviewerAdapter.init()
            adapter?.start()

        }
        
        // Listen for when a controller is connected or disconnected
        NotificationCenter.default.addObserver(self, selector: #selector(connectControllers), name: NSNotification.Name.GCControllerDidConnect, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(disconnectControllers), name: NSNotification.Name.GCControllerDidDisconnect, object: nil)
        connectControllers()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        DJIVideoPreviewer.instance()?.setView(fpvView)
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        
        // Call unSetView during exiting to release the memory.
        DJIVideoPreviewer.instance()?.unSetView()

        if adapter != nil {
            adapter?.stop()
            adapter = nil
        }
    }
    
    @IBAction func enableVirtualSticks(_ sender: UIButton) {
        toggleVirtualSticks(enabled: true)
    }
    
    @IBAction func disableVirtualSticks(_ sender: UIButton) {
        toggleVirtualSticks(enabled: false)
    }
    
    // Handles enabling/disabling the virtual sticks
    private func toggleVirtualSticks(enabled: Bool) {
        
        print("Toggling virtual sticks")
            
        // Enable or disable the virtual sticks
        self.flightController?.setVirtualStickModeEnabled(enabled, withCompletion: { (error: Error?) in
            
            // If there's an error let's stop
            if (error != nil) {
                print(error.debugDescription)
                return
            }
            
            print("Are virtual sticks enabled? \(enabled)")
            
            // Begin the virtual stick timer
            if (enabled) {

                // Schedule the timer at 20Hz while the default specified for DJI is between 5 and 25Hz
                self.timer = Timer.scheduledTimer(timeInterval: 0.05, target: self, selector: #selector(self.timerLoop), userInfo: nil, repeats: true)
                
            // Disable the virtual stick timer
            } else {
                
                self.timer?.invalidate()
                
            }
            
        })
        
    }
    
    // Handles sending control data to the flight controller
    @objc func timerLoop() {
        // Construct the flight control data object
        var controlData = DJIVirtualStickFlightControlData()
        controlData.verticalThrottle = throttle // in m/s
        controlData.roll = roll
        controlData.pitch = pitch
        controlData.yaw = yaw
        
        print("Throttle: \(throttle), Roll: \(roll), Pitch: \(pitch), Yaw: \(yaw)")
        
        // Send the control data to the FC
        self.flightController?.send(controlData, withCompletion: { (error: Error?) in
            
            // There's an error so let's stop
            if error != nil {
                
                print("Error sending data")
                
                // Disable the timer
                self.timer?.invalidate()
            }
            
        })
    }
    
    
    // Called when a controller is connected
    @objc func connectControllers() {
        // Run through each controller currently connected to the system
        for controller in GCController.controllers() {
            //Check to see whether it is an extended Game Controller (Such as a Nimbus)
            if controller.extendedGamepad != nil {
                setupController(controller: controller)
            }
        }
    }
    
    // Enumerate controllers and setup handler for sticks/buttons
    func setupController(controller: GCController) {
        controller.extendedGamepad?.valueChangedHandler = { (gamepad: GCExtendedGamepad, element: GCControllerElement) in
            self.controllerInputDetected(gamepad: gamepad, element: element, index: controller.playerIndex.rawValue)
        }
    }
    
    // Called when sticks are moved and buttons are pressed
    func controllerInputDetected(gamepad: GCExtendedGamepad, element: GCControllerElement, index: Int) {
        switch element {
            
        // Left thumbstick handles throttle and yaw
        case gamepad.leftThumbstick:
            yaw = gamepad.leftThumbstick.xAxis.value * 45.0
            throttle = gamepad.leftThumbstick.yAxis.value * 3.0
            
        // Right thumbstick handles pitch and roll
        case gamepad.rightThumbstick:
            roll = gamepad.rightThumbstick.yAxis.value * 3.0
            pitch = gamepad.rightThumbstick.xAxis.value * 3.0
            
        // Take off with left trigger
        case gamepad.leftTrigger:
            
            // Trigger will fire multiple times and we only want to send the takeoff command once
            if (!takeOffInProgress) {
                print("Trying to takeoff")
                takeOffInProgress = true
                self.flightController?.startTakeoff(completion: { (error: Error?) in
                    if error == nil {
                        self.toggleVirtualSticks(enabled: true)
                    } else {
                        print("Error taking off")
                    }
                })
            }
            
        // Land with right trigger
        case gamepad.rightTrigger:
            
            if (!landInProgress) {
                print("Trying to land")
                landInProgress = true
                self.flightController?.startLanding(completion: { (error: Error?) in
                    if error == nil {
                        self.toggleVirtualSticks(enabled: false)
                    } else {
                        print("Error landing")
                    }
                })
            }
        default:
            print("Do nothing")
        }
    }
    
    // Called when a controller is disconnected
    @objc func disconnectControllers() {
        
        // Maybe disable virtual sticks here?
        
    }
    
    private func sendControlData(x: Float, y: Float, z: Float) {
        print("Sending x: \(x), y: \(y), z: \(z), yaw: \(yaw)")
        
        // Construct the flight control data object
        var controlData = DJIVirtualStickFlightControlData()
        controlData.verticalThrottle = 0 // in m/s
        controlData.roll = 0
        controlData.pitch = 0
        controlData.yaw = 0
        
        // Send the control data to the FC
        self.flightController?.send(controlData, withCompletion: { (error: Error?) in
            
            // There's an error so let's stop
            if error != nil {
                
                print("Error sending data")
            }
            
        })
    }

}
