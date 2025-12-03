"""
Tremors Core Sensing Components Implementation
=============================================

Implements the four core modalities:
1. Voice Recognition Module
2. Gesture Recognition Framework  
3. Emotion Detection System
4. Spatial Recognition Capabilities
"""

import asyncio
import numpy as np
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingLocation(Enum):
    EDGE = "edge"
    CLOUD = "cloud"
    HYBRID = "hybrid"

class DataPrivacy(Enum):
    ON_DEVICE = "on_device"
    ENCRYPTED = "encrypted"
    ANONYMIZED = "anonymized"
    AGGREGATED = "aggregated"

@dataclass
class SensorData:
    """Base sensor data structure"""
    sensor_id: str
    timestamp: float
    modality: str
    data: Any
    metadata: Dict[str, Any]
    privacy_level: DataPrivacy
    quality_score: float = 0.0

@dataclass
class RecognitionResult:
    """Base recognition result structure"""
    modality: str
    confidence: float
    result: Any
    timestamp: float
    processing_time: float
    privacy_level: DataPrivacy

class PrivacyManager:
    """Manages privacy controls for different data types"""
    
    @staticmethod
    def apply_privacy_protection(data: Any, privacy_level: DataPrivacy) -> Any:
        """Apply privacy protection based on level"""
        if privacy_level == DataPrivacy.ON_DEVICE:
            # Keep data on device, don't transmit
            return None
        elif privacy_level == DataPrivacy.ANONYMIZED:
            # Remove personal identifiers
            return PrivacyManager._anonymize_data(data)
        elif privacy_level == DataPrivacy.AGGREGATED:
            # Aggregate and summarize data
            return PrivacyManager._aggregate_data(data)
        else:
            return data
    
    @staticmethod
    def _anonymize_data(data: Any) -> Any:
        """Anonymize sensitive data"""
        if isinstance(data, dict):
            anonymized = {}
            for key, value in data.items():
                if 'personal' in key.lower() or 'name' in key.lower():
                    anonymized[key] = "ANONYMIZED"
                else:
                    anonymized[key] = PrivacyManager._anonymize_data(value)
            return anonymized
        return data
    
    @staticmethod
    def _aggregate_data(data: Any) -> Any:
        """Aggregate data for privacy"""
        # Simple aggregation example
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], (int, float)):
                return {
                    'mean': np.mean(data),
                    'std': np.std(data),
                    'count': len(data)
                }
        return data

class VoiceRecognitionModule:
    """Advanced voice recognition with privacy controls"""
    
    def __init__(self, privacy_level: DataPrivacy = DataPrivacy.ON_DEVICE):
        self.privacy_level = privacy_level
        self.is_processing = False
        self.sample_rate = 16000
        self.buffer_size = 1024
        self.voice_activity_threshold = 0.001
        self.confidence_threshold = 0.7
        
    async def capture_audio(self, duration: float = 1.0) -> SensorData:
        """Capture audio data from microphone"""
        # Simulate audio capture
        await asyncio.sleep(0.01)  # Simulate I/O delay
        
        # Generate mock audio data
        audio_data = np.random.normal(0, 0.1, int(self.sample_rate * duration))
        
        return SensorData(
            sensor_id="voice_primary",
            timestamp=time.time(),
            modality="voice",
            data=audio_data,
            metadata={
                "sample_rate": self.sample_rate,
                "duration": duration,
                "format": "PCM"
            },
            privacy_level=self.privacy_level
        )
    
    async def preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Preprocess audio data"""
        # Simulate audio preprocessing
        await asyncio.sleep(0.05)  # Simulate processing delay
        
        # Simple preprocessing (normalize, noise reduction simulation)
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        return audio_data
    
    def extract_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract audio features using MFCC simulation"""
        # Simulate MFCC feature extraction
        # In real implementation, would use librosa or similar
        
        frame_length = 512
        hop_length = 256
        num_mfcc = 13
        
        frames = self._frame_signal(audio_data, frame_length, hop_length)
        features = np.random.random((len(frames), num_mfcc))
        
        return features
    
    def _frame_signal(self, signal: np.ndarray, frame_length: int, hop_length: int) -> np.ndarray:
        """Frame signal into windows"""
        frames = []
        for i in range(0, len(signal) - frame_length + 1, hop_length):
            frames.append(signal[i:i + frame_length])
        return np.array(frames)
    
    def recognize_speech(self, features: np.ndarray) -> RecognitionResult:
        """Perform speech recognition using simulated model"""
        start_time = time.time()
        
        # Simulate neural network inference
        # In real implementation, would use actual speech recognition model
        simulated_logits = np.random.random(1000)  # Simulate vocabulary
        predicted_word_idx = np.argmax(simulated_logits)
        confidence = float(np.max(simulated_logits))
        
        # Simulate vocabulary (just for demo)
        vocab = ["hello", "world", "tremors", "multimodal", "recognition", "privacy"]
        if predicted_word_idx < len(vocab):
            recognized_text = vocab[predicted_word_idx]
        else:
            recognized_text = f"word_{predicted_word_idx}"
        
        processing_time = time.time() - start_time
        
        return RecognitionResult(
            modality="voice",
            confidence=confidence,
            result={"text": recognized_text, "word_index": predicted_word_idx},
            timestamp=time.time(),
            processing_time=processing_time,
            privacy_level=DataPrivacy.ON_DEVICE
        )
    
    async def process_voice_input(self) -> RecognitionResult:
        """Complete voice processing pipeline"""
        logger.info("Starting voice recognition...")
        
        # Capture audio
        audio_data = await self.capture_audio()
        
        # Preprocess
        processed_audio = await self.preprocess_audio(audio_data.data)
        
        # Extract features
        features = self.extract_features(processed_audio)
        
        # Apply privacy protection
        protected_features = PrivacyManager.apply_privacy_protection(
            features, self.privacy_level
        )
        
        # Perform recognition
        if protected_features is not None:
            result = self.recognize_speech(protected_features)
        else:
            # On-device processing only
            result = self.recognize_speech(features)
        
        logger.info(f"Voice recognition completed: {result.result['text']} (confidence: {result.confidence:.2f})")
        return result

class GestureRecognitionFramework:
    """Advanced gesture recognition using computer vision"""
    
    def __init__(self, privacy_level: DataPrivacy = DataPrivacy.ANONYMIZED):
        self.privacy_level = privacy_level
        self.frame_width = 640
        self.frame_height = 480
        self.frame_rate = 30
        self.skeleton_points = 33  # MediaPipe skeleton points
        self.confidence_threshold = 0.7
        
    async def capture_video_frame(self) -> SensorData:
        """Capture video frame from camera"""
        # Simulate video capture
        await asyncio.sleep(1.0 / self.frame_rate)
        
        # Generate mock frame
        frame = np.random.randint(0, 255, (self.frame_height, self.frame_width, 3), dtype=np.uint8)
        
        return SensorData(
            sensor_id="gesture_primary",
            timestamp=time.time(),
            modality="gesture",
            data=frame,
            metadata={
                "width": self.frame_width,
                "height": self.frame_height,
                "channels": 3,
                "format": "BGR"
            },
            privacy_level=self.privacy_level
        )
    
    async def detect_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """Detect human landmarks using MediaPipe simulation"""
        # Simulate landmark detection
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Generate mock skeleton points (33 points with x, y, z, visibility)
        landmarks = np.random.random((self.skeleton_points, 4))
        landmarks[:, 0] = landmarks[:, 0] * self.frame_width  # x coordinates
        landmarks[:, 1] = landmarks[:, 1] * self.frame_height  # y coordinates
        landmarks[:, 2] = landmarks[:, 2] * 2 - 1  # z coordinates (-1 to 1)
        landmarks[:, 3] = np.random.random(self.skeleton_points)  # visibility
        
        return landmarks
    
    def preprocess_landmarks(self, landmarks: np.ndarray) -> np.ndarray:
        """Preprocess landmarks for gesture recognition"""
        # Normalize landmarks relative to body center
        center_x = landmarks[11, 0] if len(landmarks) > 11 else self.frame_width // 2
        center_y = landmarks[11, 1] if len(landmarks) > 11 else self.frame_height // 2
        
        # Center normalization
        normalized_landmarks = landmarks.copy()
        normalized_landmarks[:, 0] = (normalized_landmarks[:, 0] - center_x) / self.frame_width
        normalized_landmarks[:, 1] = (normalized_landmarks[:, 1] - center_y) / self.frame_height
        
        return normalized_landmarks
    
    def classify_gesture(self, landmarks: np.ndarray) -> RecognitionResult:
        """Classify gesture using simplified ML model simulation"""
        start_time = time.time()
        
        # Simulate gesture classification
        # Predefined gestures: wave, point, thumbs_up, peace, fist, open_hand
        gesture_classes = ["wave", "point", "thumbs_up", "peace", "fist", "open_hand"]
        
        # Simple hand gesture detection based on hand landmarks (indices 17-21)
        if len(landmarks) >= 22:
            hand_landmarks = landmarks[17:22, :]
            
            # Simple heuristic for thumbs up detection
            thumb_tip = hand_landmarks[4, :2]  # thumb tip
            thumb_ip = hand_landmarks[3, :2]   # thumb intermediate
            
            # For demo, use a more sophisticated simulation
            features = []
            for i in range(len(landmarks)):
                features.extend([landmarks[i, 0], landmarks[i, 1], landmarks[i, 3]])
            
            # Simulate neural network inference
            scores = np.random.random(len(gesture_classes))
            predicted_gesture_idx = np.argmax(scores)
            confidence = float(np.max(scores))
            
        else:
            predicted_gesture_idx = np.random.randint(len(gesture_classes))
            confidence = np.random.random()
        
        processing_time = time.time() - start_time
        
        return RecognitionResult(
            modality="gesture",
            confidence=confidence,
            result={
                "gesture": gesture_classes[predicted_gesture_idx],
                "gesture_index": predicted_gesture_idx,
                "landmarks_count": len(landmarks)
            },
            timestamp=time.time(),
            processing_time=processing_time,
            privacy_level=self.privacy_level
        )
    
    async def process_gesture_input(self) -> RecognitionResult:
        """Complete gesture processing pipeline"""
        logger.info("Starting gesture recognition...")
        
        # Capture frame
        frame_data = await self.capture_video_frame()
        
        # Detect landmarks
        landmarks = await self.detect_landmarks(frame_data.data)
        
        # Preprocess landmarks
        processed_landmarks = self.preprocess_landmarks(landmarks)
        
        # Apply privacy protection
        protected_landmarks = PrivacyManager.apply_privacy_protection(
            processed_landmarks, self.privacy_level
        )
        
        # Classify gesture
        if protected_landmarks is not None:
            result = self.classify_gesture(protected_landmarks)
        else:
            # Use anonymized version
            result = self.classify_gesture(processed_landmarks)
        
        logger.info(f"Gesture recognition completed: {result.result['gesture']} (confidence: {result.confidence:.2f})")
        return result

class EmotionDetectionSystem:
    """Advanced emotion detection using multimodal analysis"""
    
    def __init__(self, privacy_level: DataPrivacy = DataPrivacy.ANONYMIZED):
        self.privacy_level = privacy_level
        self.emotion_classes = ["happy", "sad", "angry", "surprised", "fearful", "disgusted", "neutral", "contempt"]
        self.confidence_threshold = 0.6
        self.fusion_weights = {
            "facial": 0.4,
            "vocal": 0.3,
            "gesture": 0.2,
            "contextual": 0.1
        }
    
    async def detect_facial_emotion(self, face_image: np.ndarray) -> Dict[str, float]:
        """Detect emotion from facial expression"""
        await asyncio.sleep(0.05)  # Simulate processing time
        
        # Simulate facial emotion detection
        # In real implementation, would use CNN-based FER models
        scores = np.random.random(len(self.emotion_classes))
        scores = scores / np.sum(scores)  # Normalize to probability
        
        return {emotion: float(score) for emotion, score in zip(self.emotion_classes, scores)}
    
    async def analyze_vocal_emotion(self, audio_features: np.ndarray) -> Dict[str, float]:
        """Analyze emotion from vocal features"""
        await asyncio.sleep(0.03)  # Simulate processing time
        
        # Simulate vocal emotion analysis
        # Extract prosodic features (pitch, energy, tempo)
        pitch = np.mean(audio_features) if len(audio_features) > 0 else 0.5
        energy = np.std(audio_features) if len(audio_features) > 0 else 0.5
        
        # Simulate emotion scores based on prosodic features
        scores = np.random.random(len(self.emotion_classes))
        scores = scores / np.sum(scores)
        
        return {emotion: float(score) for emotion, score in zip(self.emotion_classes, scores)}
    
    async def analyze_gesture_emotion(self, gesture_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze emotion from gesture patterns"""
        await asyncio.sleep(0.02)  # Simulate processing time
        
        # Simulate gesture-based emotion analysis
        gesture_type = gesture_data.get("gesture", "neutral")
        
        # Map gestures to emotion tendencies
        gesture_emotion_map = {
            "wave": "happy",
            "point": "neutral", 
            "thumbs_up": "happy",
            "peace": "neutral",
            "fist": "angry",
            "open_hand": "surprised"
        }
        
        # Generate emotion scores
        scores = np.random.random(len(self.emotion_classes))
        
        # Boost scores for mapped emotions
        mapped_emotion = gesture_emotion_map.get(gesture_type, "neutral")
        emotion_idx = self.emotion_classes.index(mapped_emotion)
        scores[emotion_idx] *= 1.5
        
        scores = scores / np.sum(scores)
        
        return {emotion: float(score) for emotion, score in zip(self.emotion_classes, scores)}
    
    def fuse_emotion_predictions(self, 
                               facial_emotions: Dict[str, float],
                               vocal_emotions: Dict[str, float], 
                               gesture_emotions: Dict[str, float]) -> RecognitionResult:
        """Fuse multimodal emotion predictions"""
        start_time = time.time()
        
        # Weighted fusion of emotion predictions
        fused_emotions = {}
        
        for emotion in self.emotion_classes:
            score = (
                self.fusion_weights["facial"] * facial_emotions.get(emotion, 0) +
                self.fusion_weights["vocal"] * vocal_emotions.get(emotion, 0) +
                self.fusion_weights["gesture"] * gesture_emotions.get(emotion, 0)
            )
            fused_emotions[emotion] = score
        
        # Find dominant emotion
        dominant_emotion = max(fused_emotions.keys(), key=lambda k: fused_emotions[k])
        confidence = float(fused_emotions[dominant_emotion])
        
        processing_time = time.time() - start_time
        
        return RecognitionResult(
            modality="emotion",
            confidence=confidence,
            result={
                "primary_emotion": dominant_emotion,
                "emotion_scores": fused_emotions,
                "fused": True
            },
            timestamp=time.time(),
            processing_time=processing_time,
            privacy_level=self.privacy_level
        )
    
    async def process_emotion_detection(self, 
                                      face_image: np.ndarray,
                                      audio_features: np.ndarray,
                                      gesture_data: Dict[str, Any]) -> RecognitionResult:
        """Complete emotion detection pipeline"""
        logger.info("Starting multimodal emotion detection...")
        
        # Run all emotion detection modules concurrently
        facial_task = self.detect_facial_emotion(face_image)
        vocal_task = self.analyze_vocal_emotion(audio_features)
        gesture_task = self.analyze_gesture_emotion(gesture_data)
        
        facial_emotions, vocal_emotions, gesture_emotions = await asyncio.gather(
            facial_task, vocal_task, gesture_task
        )
        
        # Apply privacy protection
        protected_facial = PrivacyManager.apply_privacy_protection(
            facial_emotions, self.privacy_level
        )
        protected_vocal = PrivacyManager.apply_privacy_protection(
            vocal_emotions, self.privacy_level
        )
        protected_gesture = PrivacyManager.apply_privacy_protection(
            gesture_emotions, self.privacy_level
        )
        
        # Fuse predictions
        result = self.fuse_emotion_predictions(
            protected_facial or facial_emotions,
            protected_vocal or vocal_emotions,
            protected_gesture or gesture_emotions
        )
        
        logger.info(f"Emotion detection completed: {result.result['primary_emotion']} (confidence: {result.confidence:.2f})")
        return result

class SpatialRecognitionCapabilities:
    """Advanced spatial recognition and mapping"""
    
    def __init__(self, privacy_level: DataPrivacy = DataPrivacy.AGGREGATED):
        self.privacy_level = privacy_level
        self.map_resolution = 0.1  # 10cm resolution
        self.localization_accuracy = 0.05  # 5cm accuracy
        self.max_map_size = (100, 100)  # 10m x 10m
        
    async def capture_depth_data(self) -> SensorData:
        """Capture depth information from sensors"""
        await asyncio.sleep(0.02)  # Simulate sensor capture
        
        # Generate mock depth data (640x480 depth map)
        depth_data = np.random.random((480, 640)) * 5.0  # 0-5 meters depth
        
        return SensorData(
            sensor_id="spatial_primary",
            timestamp=time.time(),
            modality="spatial",
            data=depth_data,
            metadata={
                "width": 640,
                "height": 480,
                "max_depth": 5.0,
                "resolution": self.map_resolution
            },
            privacy_level=self.privacy_level
        )
    
    def generate_point_cloud(self, depth_data: np.ndarray, camera_matrix: np.ndarray) -> np.ndarray:
        """Generate 3D point cloud from depth data"""
        # Simulate point cloud generation
        height, width = depth_data.shape
        points_3d = []
        
        # Generate grid of pixel coordinates
        u, v = np.meshgrid(np.arange(width), np.arange(height))
        
        # Project pixels to 3D space (simplified)
        z = depth_data.flatten()
        x = (u.flatten() - camera_matrix[0, 2]) * z / camera_matrix[0, 0]
        y = (v.flatten() - camera_matrix[1, 2]) * z / camera_matrix[1, 1]
        
        # Combine into point cloud
        point_cloud = np.column_stack([x, y, z])
        
        # Remove invalid points
        valid_mask = (z > 0) & (z < 10) & (~np.isnan(x)) & (~np.isnan(y)) & (~np.isnan(z))
        point_cloud = point_cloud[valid_mask]
        
        return point_cloud
    
    def estimate_pose(self, point_cloud: np.ndarray, previous_point_cloud: np.ndarray = None) -> Dict[str, float]:
        """Estimate camera/robot pose from point clouds"""
        # Simulate pose estimation
        # In real implementation, would use ICP, NDT, or other algorithms
        
        if previous_point_cloud is None:
            # Initial pose estimate
            pose = {
                "x": 0.0,
                "y": 0.0, 
                "z": 0.0,
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0
            }
        else:
            # Estimate relative pose change
            pose = {
                "x": np.random.uniform(-0.1, 0.1),
                "y": np.random.uniform(-0.1, 0.1),
                "z": np.random.uniform(-0.05, 0.05),
                "roll": np.random.uniform(-0.1, 0.1),
                "pitch": np.random.uniform(-0.1, 0.1),
                "yaw": np.random.uniform(-0.2, 0.2)
            }
        
        return pose
    
    def update_occupancy_grid(self, point_cloud: np.ndarray, pose: Dict[str, float]) -> np.ndarray:
        """Update occupancy grid map with new sensor data"""
        # Simulate occupancy grid update
        grid_width, grid_height = self.max_map_size
        
        # Generate mock occupancy grid
        occupancy_grid = np.zeros((grid_height, grid_width), dtype=np.uint8)
        
        # Mark occupied cells where points exist (simplified)
        for point in point_cloud[:100]:  # Use subset for performance
            grid_x = int(point[0] / self.map_resolution) + grid_width // 2
            grid_y = int(point[1] / self.map_resolution) + grid_height // 2
            
            if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
                occupancy_grid[grid_y, grid_x] = 100  # Mark as occupied
        
        return occupancy_grid
    
    def perform_spatial_recognition(self, depth_data: np.ndarray, pose: Dict[str, float]) -> RecognitionResult:
        """Perform complete spatial recognition"""
        start_time = time.time()
        
        # Simulate camera matrix
        camera_matrix = np.array([
            [525.0, 0, 320.0],
            [0, 525.0, 240.0], 
            [0, 0, 1]
        ])
        
        # Generate point cloud
        point_cloud = self.generate_point_cloud(depth_data, camera_matrix)
        
        # Update map
        occupancy_grid = self.update_occupancy_grid(point_cloud, pose)
        
        # Extract spatial features
        spatial_features = {
            "objects_detected": np.count_nonzero(occupancy_grid > 50),
            "coverage_area": np.count_nonzero(occupancy_grid > 0) * (self.map_resolution ** 2),
            "max_depth": float(np.max(depth_data)),
            "min_depth": float(np.min(depth_data[depth_data > 0])),
            "point_cloud_size": len(point_cloud)
        }
        
        processing_time = time.time() - start_time
        
        # Apply privacy protection
        protected_features = PrivacyManager.apply_privacy_protection(
            spatial_features, self.privacy_level
        )
        
        return RecognitionResult(
            modality="spatial",
            confidence=0.8,  # Simulated confidence
            result=protected_features or spatial_features,
            timestamp=time.time(),
            processing_time=processing_time,
            privacy_level=self.privacy_level
        )
    
    async def process_spatial_input(self) -> RecognitionResult:
        """Complete spatial recognition pipeline"""
        logger.info("Starting spatial recognition...")
        
        # Capture depth data
        depth_data = await self.capture_depth_data()
        
        # Estimate pose (simplified - would track pose over time in real system)
        pose = self.estimate_pose(depth_data.data)
        
        # Perform spatial recognition
        result = self.perform_spatial_recognition(depth_data.data, pose)
        
        logger.info(f"Spatial recognition completed (confidence: {result.confidence:.2f})")
        return result

class MultimodalSensingCore:
    """Main class that orchestrates all sensing modalities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize sensing modules
        self.voice_module = VoiceRecognitionModule(
            privacy_level=DataPrivacy.ON_DEVICE
        )
        self.gesture_framework = GestureRecognitionFramework(
            privacy_level=DataPrivacy.ANONYMIZED
        )
        self.emotion_system = EmotionDetectionSystem(
            privacy_level=DataPrivacy.ANONYMIZED
        )
        self.spatial_capabilities = SpatialRecognitionCapabilities(
            privacy_level=DataPrivacy.AGGREGATED
        )
        
        self.is_processing = False
        self.processing_lock = threading.Lock()
    
    async def process_all_modalities(self) -> Dict[str, RecognitionResult]:
        """Process all modalities concurrently"""
        with self.processing_lock:
            if self.is_processing:
                logger.warning("Processing already in progress")
                return {}
            
            self.is_processing = True
        
        try:
            logger.info("Starting multimodal processing...")
            start_time = time.time()
            
            # Create mock input data for demonstration
            mock_face_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            mock_audio_features = np.random.random(100)
            mock_gesture_data = {"gesture": "wave", "confidence": 0.8}
            
            # Process all modalities concurrently
            voice_task = self.voice_module.process_voice_input()
            gesture_task = self.gesture_framework.process_gesture_input()
            emotion_task = self.emotion_system.process_emotion_detection(
                mock_face_image, mock_audio_features, mock_gesture_data
            )
            spatial_task = self.spatial_capabilities.process_spatial_input()
            
            # Wait for all to complete
            results = await asyncio.gather(
                voice_task, gesture_task, emotion_task, spatial_task,
                return_exceptions=True
            )
            
            # Organize results
            recognition_results = {}
            for i, (modality, result) in enumerate([
                ("voice", results[0]),
                ("gesture", results[1]), 
                ("emotion", results[2]),
                ("spatial", results[3])
            ]):
                if not isinstance(result, Exception):
                    recognition_results[modality] = result
                else:
                    logger.error(f"{modality} processing failed: {result}")
                    recognition_results[modality] = None
            
            total_time = time.time() - start_time
            logger.info(f"Multimodal processing completed in {total_time:.2f}s")
            
            return recognition_results
            
        finally:
            self.is_processing = False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all modules"""
        return {
            "voice": {
                "privacy_level": self.voice_module.privacy_level.value,
                "sample_rate": self.voice_module.sample_rate
            },
            "gesture": {
                "privacy_level": self.gesture_framework.privacy_level.value,
                "frame_rate": self.gesture_framework.frame_rate
            },
            "emotion": {
                "privacy_level": self.emotion_system.privacy_level.value,
                "fusion_weights": self.emotion_system.fusion_weights
            },
            "spatial": {
                "privacy_level": self.spatial_capabilities.privacy_level.value,
                "map_resolution": self.spatial_capabilities.map_resolution
            }
        }

if __name__ == "__main__":
    # Test the multimodal sensing core
    async def test_sensing_core():
        print("🚀 Testing Tremors Multimodal Sensing Core...")
        
        # Create configuration
        config = {
            "enable_voice": True,
            "enable_gesture": True,
            "enable_emotion": True,
            "enable_spatial": True,
            "privacy_level": "anonymized"
        }
        
        # Initialize core
        core = MultimodalSensingCore(config)
        
        # Test all modalities
        results = await core.process_all_modalities()
        
        # Print results
        print("\n📊 Recognition Results:")
        for modality, result in results.items():
            if result:
                print(f"  {modality.upper()}:")
                print(f"    Confidence: {result.confidence:.3f}")
                print(f"    Processing Time: {result.processing_time:.3f}s")
                print(f"    Result: {result.result}")
        
        # Print performance metrics
        metrics = core.get_performance_metrics()
        print("\n🔧 Performance Metrics:")
        for modality, metric in metrics.items():
            print(f"  {modality.upper()}: {metric}")
    
    # Run the test
    asyncio.run(test_sensing_core())
