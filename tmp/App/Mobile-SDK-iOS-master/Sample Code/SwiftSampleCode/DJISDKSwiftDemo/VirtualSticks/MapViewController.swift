//
//  MapViewController.swift
//  DJISDKSwiftDemo
//
//  Created by Dennis Baldwin on 8/9/20.
//  Copyright © 2020 DJI. All rights reserved.
//

import UIKit
import Mapbox

class MapViewController: UIViewController {
    
    var mapView: MGLMapView!
    var aircraftMarker: MGLPointAnnotation!
    var tapMarker: MGLPointAnnotation!

    override func viewDidLoad() {
        super.viewDidLoad()

        print("loading map");
        let url = URL(string: "mapbox://styles/mapbox/streets-v11")
        mapView = MGLMapView(frame: view.bounds, styleURL: url)
        mapView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        mapView.setCenter(CLLocationCoordinate2D(latitude: 32, longitude: -98), animated: false)
        mapView.setZoomLevel(13, animated: false)
        view.addSubview(mapView)
        
        aircraftMarker = MGLPointAnnotation()
        aircraftMarker.coordinate = CLLocationCoordinate2D(latitude: 32, longitude: -98)
        mapView.addAnnotation(aircraftMarker)
        
        startStopListeningCoordinates(shouldListen: true)
        
        // Listen for map tap
        let singleTap = UITapGestureRecognizer(target: self, action: #selector(handleMapTap(sender:)))
        
        for recognizer in mapView.gestureRecognizers! where recognizer is UITapGestureRecognizer {
            singleTap.require(toFail: recognizer)
        }
        
        mapView.addGestureRecognizer(singleTap)
         
    }
    
    override func viewWillAppear(_ animated: Bool) {
        navigationController?.setNavigationBarHidden(true, animated: animated)
    }
    
    override func viewDidDisappear(_ animated: Bool) {
        startStopListeningCoordinates(shouldListen: false)
    }
    
    func startStopListeningCoordinates(shouldListen: Bool) {
        let locationKey = DJIFlightControllerKey(param: DJIFlightControllerParamAircraftLocation)
        
        if !shouldListen {
            // At anytime, you may stop listening to a key or to all key for a given listener
            DJISDKManager.keyManager()?.stopListening(on: locationKey!, ofListener: self)
            //self.listeningCoordinatesLabel.text = "Stopped";
        } else {
            // Start listening is as easy as passing a block with a key.
            // Note that start listening won't do a get. Your block will be executed
            // the next time the associated data is being pulled.
            DJISDKManager.keyManager()?.startListeningForChanges(on: locationKey!, withListener: self, andUpdate: { (oldValue: DJIKeyedValue?, newValue: DJIKeyedValue?) in
                if newValue != nil {
                    // DJIFlightControllerParamAircraftLocation is associated with a DJISDKLocation object
                    let aircraftCoordinates = newValue!.value! as! CLLocation
                    
                    self.mapView.setCenter(CLLocationCoordinate2D(latitude: aircraftCoordinates.coordinate.latitude, longitude: aircraftCoordinates.coordinate.longitude), animated: false)
                    
                    self.aircraftMarker.coordinate = CLLocationCoordinate2D(latitude: aircraftCoordinates.coordinate.latitude, longitude: aircraftCoordinates.coordinate.longitude)
                    
                    print(aircraftCoordinates)
                    //self.listeningCoordinatesLabel.text = "Lat: \(aircraftCoordinates.coordinate.latitude) - Long: \(aircraftCoordinates.coordinate.longitude)"
                }
            })
            //self.listeningCoordinatesLabel.text = "Started...";
        }
        
    }
    
    @objc @IBAction func handleMapTap(sender: UITapGestureRecognizer) {
        let tapPoint: CGPoint = sender.location(in: mapView)
        print(tapPoint)
        let tapCoordinate: CLLocationCoordinate2D = mapView.convert(tapPoint, toCoordinateFrom: nil)
        
        tapMarker = MGLPointAnnotation()
        tapMarker.coordinate = tapCoordinate
        mapView.addAnnotation(tapMarker)
        
        print(getBearingBetweenTwoPoints(point1: aircraftMarker.coordinate, point2: tapMarker.coordinate))
        
    }
    
    func degreesToRadians(degrees: Double) -> Double { return degrees * .pi / 180.0 }
    func radiansToDegrees(radians: Double) -> Double { return radians * 180.0 / .pi }

    func getBearingBetweenTwoPoints(point1 : CLLocationCoordinate2D, point2 : CLLocationCoordinate2D) -> Double {

        let lat1 = degreesToRadians(degrees: point1.latitude)
        let lon1 = degreesToRadians(degrees: point1.longitude)

        let lat2 = degreesToRadians(degrees: point2.latitude)
        let lon2 = degreesToRadians(degrees: point2.longitude)

        let dLon = lon2 - lon1

        let y = sin(dLon) * cos(lat2)
        let x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        let radiansBearing = atan2(y, x)

        return radiansToDegrees(radians: radiansBearing)
    }

}
