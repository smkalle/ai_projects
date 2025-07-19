#!/usr/bin/env python3
"""
Program 30: Digital Twin Platform - Edge Computing Server
Raspberry Pi 4 Edge Computing Server for Digital Twin Platform

Comprehensive edge computing system implementing physics-based modeling,
real-time simulation, machine learning inference, and bi-directional
control for Industry 4.0 digital twin applications.

Features:
- Multi-physics simulation engine (thermal, mechanical, fluid dynamics)
- Real-time sensor data synchronization (<100ms latency)
- Machine learning model inference and training
- Process optimization algorithms
- Predictive maintenance analytics
- Quality prediction and control
- Cloud connectivity and data management
- RESTful API for system integration
- WebSocket real-time communication
- MQTT broker for IoT device communication

Hardware: Raspberry Pi 4 8GB + High-speed storage + Industrial I/O
Dependencies: NumPy, SciPy, TensorFlow, Flask, MQTT, InfluxDB
"""

import asyncio
import json
import logging
import multiprocessing
import time
import numpy as np
import pandas as pd
import sqlite3
import threading
from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Core libraries
import serial
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request, websocket
from flask_socketio import SocketIO, emit
import redis
import psutil

# Scientific computing
from scipy import optimize, signal, interpolate
from scipy.integrate import odeint, solve_ivp
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Deep learning
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("TensorFlow not available - using scikit-learn models only")

# Configuration
DEVICE_ID = "RPI_EDGE_SERVER_001"
VERSION = "2.0"
DEBUG = True

# Hardware configuration
SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUDRATE = 921600
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Performance targets
SYNC_LATENCY_TARGET = 100  # milliseconds
MODEL_ACCURACY_TARGET = 0.95
PREDICTION_HORIZON = 24 * 3600  # 24 hours in seconds
MAX_DATA_BUFFER_SIZE = 10000

# Physics simulation parameters
THERMAL_DIFFUSIVITY = 1.4e-7  # m^2/s for steel
ELASTIC_MODULUS = 200e9  # Pa for steel
POISSON_RATIO = 0.3
DENSITY = 7850  # kg/m^3 for steel

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/digital_twin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SensorData:
    """Data structure for sensor readings"""
    timestamp: float
    device_id: str
    temperatures: List[float]
    pressures: List[float]
    vibrations: List[float]
    power: Dict[str, float]
    positions: List[float]
    forces: List[float]
    data_quality: float
    
@dataclass
class ProcessState:
    """Data structure for manufacturing process state"""
    process_id: str
    process_type: str
    active: bool
    cycle_time: float
    target_cycle_time: float
    efficiency: float
    quality_score: float
    parameters: Dict[str, float]
    
@dataclass
class PhysicsState:
    """Data structure for physics simulation state"""
    temperature_field: np.ndarray
    stress_field: np.ndarray
    displacement_field: np.ndarray
    velocity_field: np.ndarray
    material_properties: Dict[str, float]
    boundary_conditions: Dict[str, Any]
    
@dataclass
class Prediction:
    """Data structure for predictions"""
    process_id: str
    predicted_quality: float
    predicted_cycle_time: float
    predicted_defect_rate: float
    maintenance_probability: float
    energy_forecast: float
    confidence: float
    timestamp: float

class PhysicsEngine:
    """Multi-physics simulation engine for digital twin"""
    
    def __init__(self):
        self.thermal_model = ThermalModel()
        self.mechanical_model = MechanicalModel()
        self.fluid_model = FluidModel()
        self.material_model = MaterialModel()
        self.simulation_time = 0.0
        self.time_step = 0.1  # seconds
        
    def update(self, sensor_data: SensorData, dt: float) -> PhysicsState:
        """Update all physics models with new sensor data"""
        try:
            # Update thermal model
            thermal_state = self.thermal_model.update(sensor_data, dt)
            
            # Update mechanical model
            mechanical_state = self.mechanical_model.update(sensor_data, dt)
            
            # Update fluid model
            fluid_state = self.fluid_model.update(sensor_data, dt)
            
            # Update material properties
            material_state = self.material_model.update(sensor_data, dt)
            
            # Combine all physics states
            physics_state = PhysicsState(
                temperature_field=thermal_state['temperature'],
                stress_field=mechanical_state['stress'],
                displacement_field=mechanical_state['displacement'],
                velocity_field=fluid_state['velocity'],
                material_properties=material_state,
                boundary_conditions={
                    'thermal': thermal_state['boundary_conditions'],
                    'mechanical': mechanical_state['boundary_conditions'],
                    'fluid': fluid_state['boundary_conditions']
                }
            )
            
            self.simulation_time += dt
            return physics_state
            
        except Exception as e:
            logger.error(f"Physics engine update failed: {e}")
            return self._get_default_state()
    
    def _get_default_state(self) -> PhysicsState:
        """Return default physics state in case of error"""
        return PhysicsState(
            temperature_field=np.zeros((10, 10)),
            stress_field=np.zeros((10, 10)),
            displacement_field=np.zeros((10, 10)),
            velocity_field=np.zeros((10, 10)),
            material_properties={'E': ELASTIC_MODULUS, 'nu': POISSON_RATIO},
            boundary_conditions={}
        )

class ThermalModel:
    """Thermal physics simulation model"""
    
    def __init__(self, grid_size: Tuple[int, int] = (50, 50)):
        self.grid_size = grid_size
        self.temperature_field = np.ones(grid_size) * 25.0  # Initial temperature 25°C
        self.previous_temperature = self.temperature_field.copy()
        self.thermal_conductivity = 50.0  # W/m·K for steel
        self.specific_heat = 460.0  # J/kg·K for steel
        self.density = DENSITY
        
    def update(self, sensor_data: SensorData, dt: float) -> Dict[str, Any]:
        """Update thermal field using finite difference method"""
        try:
            # Extract temperature measurements
            temp_measurements = sensor_data.temperatures
            
            # Apply boundary conditions from sensor measurements
            if len(temp_measurements) >= 4:
                # Apply temperatures at boundaries
                self.temperature_field[0, :] = temp_measurements[0]  # Top boundary
                self.temperature_field[-1, :] = temp_measurements[1]  # Bottom boundary
                self.temperature_field[:, 0] = temp_measurements[2]  # Left boundary
                self.temperature_field[:, -1] = temp_measurements[3]  # Right boundary
            
            # Heat generation from processes
            heat_generation = self._calculate_heat_generation(sensor_data)
            
            # Solve 2D heat equation using finite differences
            alpha = self.thermal_conductivity / (self.density * self.specific_heat)
            dx = 0.01  # 1 cm grid spacing
            dy = 0.01
            
            # Stability condition for explicit scheme
            stability_factor = alpha * dt * (1/dx**2 + 1/dy**2)
            if stability_factor > 0.25:
                dt = 0.25 / (alpha * (1/dx**2 + 1/dy**2))
            
            # Update interior points
            for i in range(1, self.grid_size[0]-1):
                for j in range(1, self.grid_size[1]-1):
                    d2T_dx2 = (self.temperature_field[i+1, j] - 2*self.temperature_field[i, j] + 
                              self.temperature_field[i-1, j]) / dx**2
                    d2T_dy2 = (self.temperature_field[i, j+1] - 2*self.temperature_field[i, j] + 
                              self.temperature_field[i, j-1]) / dy**2
                    
                    dT_dt = alpha * (d2T_dx2 + d2T_dy2) + heat_generation[i, j]
                    self.temperature_field[i, j] += dT_dt * dt
            
            # Calculate thermal gradient
            grad_x, grad_y = np.gradient(self.temperature_field)
            thermal_gradient = np.sqrt(grad_x**2 + grad_y**2)
            
            return {
                'temperature': self.temperature_field.copy(),
                'thermal_gradient': thermal_gradient,
                'max_temperature': np.max(self.temperature_field),
                'min_temperature': np.min(self.temperature_field),
                'average_temperature': np.mean(self.temperature_field),
                'boundary_conditions': {
                    'top': temp_measurements[0] if len(temp_measurements) > 0 else 25.0,
                    'bottom': temp_measurements[1] if len(temp_measurements) > 1 else 25.0,
                    'left': temp_measurements[2] if len(temp_measurements) > 2 else 25.0,
                    'right': temp_measurements[3] if len(temp_measurements) > 3 else 25.0
                }
            }
            
        except Exception as e:
            logger.error(f"Thermal model update failed: {e}")
            return {'temperature': self.temperature_field, 'boundary_conditions': {}}
    
    def _calculate_heat_generation(self, sensor_data: SensorData) -> np.ndarray:
        """Calculate heat generation from power consumption"""
        heat_gen = np.zeros(self.grid_size)
        
        # Distribute power as heat generation
        if 'active' in sensor_data.power:
            power_density = sensor_data.power['active'] * 1000 / (0.5 * 0.5)  # W/m^2
            # Add heat sources in center region
            center_x, center_y = self.grid_size[0]//2, self.grid_size[1]//2
            heat_gen[center_x-5:center_x+5, center_y-5:center_y+5] = power_density
        
        return heat_gen

class MechanicalModel:
    """Mechanical physics simulation model"""
    
    def __init__(self, grid_size: Tuple[int, int] = (50, 50)):
        self.grid_size = grid_size
        self.displacement_field = np.zeros((grid_size[0], grid_size[1], 2))  # 2D displacement
        self.stress_field = np.zeros((grid_size[0], grid_size[1], 3))  # σx, σy, τxy
        self.strain_field = np.zeros((grid_size[0], grid_size[1], 3))  # εx, εy, γxy
        self.elastic_modulus = ELASTIC_MODULUS
        self.poisson_ratio = POISSON_RATIO
        
    def update(self, sensor_data: SensorData, dt: float) -> Dict[str, Any]:
        """Update mechanical fields using finite element approximation"""
        try:
            # Apply force boundary conditions
            forces = sensor_data.forces if sensor_data.forces else [0, 0, 0, 0]
            
            # Calculate stress from applied forces and thermal expansion
            thermal_stress = self._calculate_thermal_stress(sensor_data)
            applied_stress = self._calculate_applied_stress(forces)
            
            # Total stress field
            self.stress_field = thermal_stress + applied_stress
            
            # Calculate strain from stress using constitutive relations
            self._update_strain_field()
            
            # Calculate displacement from strain
            self._update_displacement_field()
            
            # Calculate von Mises stress
            von_mises_stress = self._calculate_von_mises_stress()
            
            # Calculate safety factor
            yield_strength = 250e6  # Pa for steel
            safety_factor = yield_strength / np.maximum(von_mises_stress, 1e6)
            
            return {
                'stress': self.stress_field.copy(),
                'strain': self.strain_field.copy(),
                'displacement': self.displacement_field.copy(),
                'von_mises_stress': von_mises_stress,
                'safety_factor': safety_factor,
                'max_stress': np.max(von_mises_stress),
                'max_displacement': np.max(np.linalg.norm(self.displacement_field, axis=2)),
                'boundary_conditions': {
                    'forces': forces,
                    'constraints': 'fixed_bottom'
                }
            }
            
        except Exception as e:
            logger.error(f"Mechanical model update failed: {e}")
            return {'stress': self.stress_field, 'displacement': self.displacement_field, 
                   'boundary_conditions': {}}
    
    def _calculate_thermal_stress(self, sensor_data: SensorData) -> np.ndarray:
        """Calculate thermal stress from temperature field"""
        stress = np.zeros_like(self.stress_field)
        
        if len(sensor_data.temperatures) >= 4:
            # Simplified thermal stress calculation
            temp_avg = np.mean(sensor_data.temperatures[:4])
            thermal_expansion_coeff = 12e-6  # 1/K for steel
            reference_temp = 25.0  # °C
            
            thermal_strain = thermal_expansion_coeff * (temp_avg - reference_temp)
            thermal_stress_magnitude = self.elastic_modulus * thermal_strain / (1 - self.poisson_ratio)
            
            # Apply thermal stress uniformly
            stress[:, :, 0] = thermal_stress_magnitude  # σx
            stress[:, :, 1] = thermal_stress_magnitude  # σy
            # τxy remains zero for uniform thermal expansion
        
        return stress
    
    def _calculate_applied_stress(self, forces: List[float]) -> np.ndarray:
        """Calculate stress from applied forces"""
        stress = np.zeros_like(self.stress_field)
        
        # Apply forces at boundaries (simplified)
        if len(forces) >= 4:
            area = 0.01  # m^2 (assumed cross-sectional area)
            
            # Force on top boundary
            if forces[0] != 0:
                stress[0, :, 1] = forces[0] / area  # σy
            
            # Force on bottom boundary
            if forces[1] != 0:
                stress[-1, :, 1] = forces[1] / area  # σy
            
            # Force on left boundary
            if forces[2] != 0:
                stress[:, 0, 0] = forces[2] / area  # σx
            
            # Force on right boundary
            if forces[3] != 0:
                stress[:, -1, 0] = forces[3] / area  # σx
        
        return stress
    
    def _update_strain_field(self):
        """Update strain field from stress using constitutive relations"""
        E = self.elastic_modulus
        nu = self.poisson_ratio
        
        # Plane stress conditions
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                σx = self.stress_field[i, j, 0]
                σy = self.stress_field[i, j, 1]
                τxy = self.stress_field[i, j, 2]
                
                # Strain components
                self.strain_field[i, j, 0] = (σx - nu * σy) / E  # εx
                self.strain_field[i, j, 1] = (σy - nu * σx) / E  # εy
                self.strain_field[i, j, 2] = τxy / (E / (2 * (1 + nu)))  # γxy
    
    def _update_displacement_field(self):
        """Update displacement field from strain (simplified)"""
        dx = 0.01  # Grid spacing in meters
        
        # Integrate strain to get displacement (simplified approach)
        for i in range(1, self.grid_size[0]):
            for j in range(self.grid_size[1]):
                self.displacement_field[i, j, 0] = (self.displacement_field[i-1, j, 0] + 
                                                   self.strain_field[i, j, 0] * dx)
        
        for i in range(self.grid_size[0]):
            for j in range(1, self.grid_size[1]):
                self.displacement_field[i, j, 1] = (self.displacement_field[i, j-1, 1] + 
                                                   self.strain_field[i, j, 1] * dx)
    
    def _calculate_von_mises_stress(self) -> np.ndarray:
        """Calculate von Mises equivalent stress"""
        σx = self.stress_field[:, :, 0]
        σy = self.stress_field[:, :, 1]
        τxy = self.stress_field[:, :, 2]
        
        von_mises = np.sqrt(σx**2 + σy**2 - σx*σy + 3*τxy**2)
        return von_mises

class FluidModel:
    """Fluid dynamics simulation model"""
    
    def __init__(self, grid_size: Tuple[int, int] = (50, 50)):
        self.grid_size = grid_size
        self.velocity_field = np.zeros((grid_size[0], grid_size[1], 2))  # u, v components
        self.pressure_field = np.zeros(grid_size)
        self.density = 1.2  # kg/m^3 for air
        self.viscosity = 1.8e-5  # Pa·s for air
        
    def update(self, sensor_data: SensorData, dt: float) -> Dict[str, Any]:
        """Update fluid fields using simplified CFD"""
        try:
            # Update pressure field from sensor data
            if len(sensor_data.pressures) >= 4:
                # Apply pressure boundary conditions
                self.pressure_field[0, :] = sensor_data.pressures[0] * 100  # Convert to Pa
                self.pressure_field[-1, :] = sensor_data.pressures[1] * 100
                self.pressure_field[:, 0] = sensor_data.pressures[2] * 100
                self.pressure_field[:, -1] = sensor_data.pressures[3] * 100
            
            # Solve simplified Navier-Stokes equations
            self._solve_velocity_field(dt)
            
            # Calculate flow properties
            velocity_magnitude = np.sqrt(self.velocity_field[:, :, 0]**2 + 
                                       self.velocity_field[:, :, 1]**2)
            
            # Calculate Reynolds number
            characteristic_length = 0.1  # m
            reynolds_number = (self.density * np.mean(velocity_magnitude) * 
                             characteristic_length / self.viscosity)
            
            return {
                'velocity': self.velocity_field.copy(),
                'pressure': self.pressure_field.copy(),
                'velocity_magnitude': velocity_magnitude,
                'reynolds_number': reynolds_number,
                'max_velocity': np.max(velocity_magnitude),
                'pressure_drop': np.max(self.pressure_field) - np.min(self.pressure_field),
                'boundary_conditions': {
                    'inlet_pressure': sensor_data.pressures[0] if len(sensor_data.pressures) > 0 else 0,
                    'outlet_pressure': sensor_data.pressures[1] if len(sensor_data.pressures) > 1 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Fluid model update failed: {e}")
            return {'velocity': self.velocity_field, 'pressure': self.pressure_field, 
                   'boundary_conditions': {}}
    
    def _solve_velocity_field(self, dt: float):
        """Solve for velocity field using pressure gradient"""
        dx = 0.01  # Grid spacing
        dy = 0.01
        
        # Calculate pressure gradients
        dpx, dpy = np.gradient(self.pressure_field, dx, dy)
        
        # Update velocity using momentum equation (simplified)
        # ∂u/∂t = -1/ρ * ∂p/∂x + ν * ∇²u
        for i in range(1, self.grid_size[0]-1):
            for j in range(1, self.grid_size[1]-1):
                # Laplacian of velocity
                d2u_dx2 = (self.velocity_field[i+1, j, 0] - 2*self.velocity_field[i, j, 0] + 
                          self.velocity_field[i-1, j, 0]) / dx**2
                d2u_dy2 = (self.velocity_field[i, j+1, 0] - 2*self.velocity_field[i, j, 0] + 
                          self.velocity_field[i, j-1, 0]) / dy**2
                
                d2v_dx2 = (self.velocity_field[i+1, j, 1] - 2*self.velocity_field[i, j, 1] + 
                          self.velocity_field[i-1, j, 1]) / dx**2
                d2v_dy2 = (self.velocity_field[i, j+1, 1] - 2*self.velocity_field[i, j, 1] + 
                          self.velocity_field[i, j-1, 1]) / dy**2
                
                kinematic_viscosity = self.viscosity / self.density
                
                # Update u-velocity
                du_dt = -dpx[i, j] / self.density + kinematic_viscosity * (d2u_dx2 + d2u_dy2)
                self.velocity_field[i, j, 0] += du_dt * dt
                
                # Update v-velocity
                dv_dt = -dpy[i, j] / self.density + kinematic_viscosity * (d2v_dx2 + d2v_dy2)
                self.velocity_field[i, j, 1] += dv_dt * dt

class MaterialModel:
    """Material properties model with temperature and stress dependence"""
    
    def __init__(self):
        self.base_properties = {
            'elastic_modulus': ELASTIC_MODULUS,
            'yield_strength': 250e6,  # Pa
            'ultimate_strength': 400e6,  # Pa
            'thermal_conductivity': 50.0,  # W/m·K
            'specific_heat': 460.0,  # J/kg·K
            'thermal_expansion': 12e-6,  # 1/K
            'fatigue_limit': 180e6  # Pa
        }
        self.current_properties = self.base_properties.copy()
        
    def update(self, sensor_data: SensorData, dt: float) -> Dict[str, float]:
        """Update material properties based on temperature and loading"""
        try:
            # Calculate average temperature
            avg_temp = np.mean(sensor_data.temperatures) if sensor_data.temperatures else 25.0
            
            # Temperature-dependent properties
            temp_factor = self._temperature_factor(avg_temp)
            
            # Update elastic modulus (decreases with temperature)
            self.current_properties['elastic_modulus'] = (self.base_properties['elastic_modulus'] * 
                                                        temp_factor)
            
            # Update yield strength (decreases with temperature)
            self.current_properties['yield_strength'] = (self.base_properties['yield_strength'] * 
                                                        temp_factor)
            
            # Update thermal conductivity (slight decrease with temperature)
            self.current_properties['thermal_conductivity'] = (self.base_properties['thermal_conductivity'] * 
                                                             (1 - 0.0005 * (avg_temp - 25)))
            
            # Calculate fatigue damage accumulation
            if len(sensor_data.forces) > 0:
                stress_amplitude = np.std(sensor_data.forces)
                fatigue_damage = self._calculate_fatigue_damage(stress_amplitude, avg_temp)
                self.current_properties['fatigue_damage'] = fatigue_damage
            
            return self.current_properties.copy()
            
        except Exception as e:
            logger.error(f"Material model update failed: {e}")
            return self.base_properties.copy()
    
    def _temperature_factor(self, temperature: float) -> float:
        """Calculate temperature-dependent material property factor"""
        # Simplified temperature dependence
        reference_temp = 25.0  # °C
        temp_coefficient = -0.0005  # 1/°C
        
        factor = 1 + temp_coefficient * (temperature - reference_temp)
        return max(0.1, factor)  # Minimum 10% of room temperature properties
    
    def _calculate_fatigue_damage(self, stress_amplitude: float, temperature: float) -> float:
        """Calculate fatigue damage accumulation using Miner's rule"""
        # Convert force to stress (simplified)
        stress = abs(stress_amplitude) * 1e6  # Assume 1 MPa per Newton
        
        # Temperature-adjusted fatigue limit
        fatigue_limit = self.base_properties['fatigue_limit'] * self._temperature_factor(temperature)
        
        if stress > fatigue_limit:
            # S-N curve parameters for steel
            fatigue_strength_coeff = 900e6  # Pa
            fatigue_strength_exponent = -0.09
            
            # Calculate cycles to failure
            cycles_to_failure = (stress / fatigue_strength_coeff) ** (1 / fatigue_strength_exponent)
            
            # Damage per cycle
            damage_per_cycle = 1.0 / max(cycles_to_failure, 1)
            return damage_per_cycle
        else:
            return 0.0  # No damage below fatigue limit

class MLEngine:
    """Machine learning engine for predictions and optimization"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_metrics = {}
        self.feature_buffer = deque(maxlen=1000)
        self.target_buffer = deque(maxlen=1000)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize ML models for different predictions"""
        # Quality prediction model
        self.models['quality'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['quality'] = StandardScaler()
        
        # Cycle time prediction model
        self.models['cycle_time'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['cycle_time'] = StandardScaler()
        
        # Maintenance prediction model
        self.models['maintenance'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['maintenance'] = StandardScaler()
        
        # Energy prediction model
        self.models['energy'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalers['energy'] = StandardScaler()
        
        # Deep learning model (if TensorFlow is available)
        if TF_AVAILABLE:
            self._initialize_deep_models()
    
    def _initialize_deep_models(self):
        """Initialize deep learning models"""
        try:
            # Quality prediction neural network
            model = keras.Sequential([
                keras.layers.Dense(128, activation='relu', input_shape=(20,)),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(1, activation='sigmoid')
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            self.models['quality_deep'] = model
            
            logger.info("Deep learning models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize deep learning models: {e}")
    
    def extract_features(self, sensor_data: SensorData, process_state: ProcessState) -> np.ndarray:
        """Extract features from sensor data and process state"""
        features = []
        
        # Temperature features
        if sensor_data.temperatures:
            features.extend([
                np.mean(sensor_data.temperatures),
                np.std(sensor_data.temperatures),
                np.max(sensor_data.temperatures),
                np.min(sensor_data.temperatures)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Vibration features
        if sensor_data.vibrations:
            features.extend([
                np.mean(sensor_data.vibrations),
                np.std(sensor_data.vibrations),
                np.max(sensor_data.vibrations)
            ])
        else:
            features.extend([0, 0, 0])
        
        # Pressure features
        if sensor_data.pressures:
            features.extend([
                np.mean(sensor_data.pressures),
                np.std(sensor_data.pressures)
            ])
        else:
            features.extend([0, 0])
        
        # Power features
        features.extend([
            sensor_data.power.get('active', 0),
            sensor_data.power.get('factor', 0),
        ])
        
        # Process features
        features.extend([
            process_state.cycle_time,
            process_state.efficiency,
            process_state.quality_score
        ])
        
        # Force features
        if sensor_data.forces:
            features.extend([
                np.mean(sensor_data.forces),
                np.std(sensor_data.forces)
            ])
        else:
            features.extend([0, 0])
        
        # Position features
        if sensor_data.positions:
            features.extend([
                np.mean(sensor_data.positions),
                np.std(sensor_data.positions)
            ])
        else:
            features.extend([0, 0])
        
        # Data quality
        features.append(sensor_data.data_quality)
        
        # Pad or truncate to exactly 20 features
        if len(features) > 20:
            features = features[:20]
        elif len(features) < 20:
            features.extend([0] * (20 - len(features)))
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, sensor_data: SensorData, process_state: ProcessState) -> Prediction:
        """Make predictions using trained models"""
        try:
            features = self.extract_features(sensor_data, process_state)
            
            # Initialize prediction with defaults
            prediction = Prediction(
                process_id=process_state.process_id,
                predicted_quality=process_state.quality_score,
                predicted_cycle_time=process_state.target_cycle_time,
                predicted_defect_rate=5.0,
                maintenance_probability=0.1,
                energy_forecast=10.0,
                confidence=0.5,
                timestamp=time.time()
            )
            
            if self.is_trained:
                # Quality prediction
                if 'quality' in self.models:
                    features_scaled = self.scalers['quality'].transform(features)
                    quality_pred = self.models['quality'].predict(features_scaled)[0]
                    prediction.predicted_quality = max(0, min(100, quality_pred))
                
                # Cycle time prediction
                if 'cycle_time' in self.models:
                    features_scaled = self.scalers['cycle_time'].transform(features)
                    cycle_time_pred = self.models['cycle_time'].predict(features_scaled)[0]
                    prediction.predicted_cycle_time = max(10, cycle_time_pred)
                
                # Maintenance prediction
                if 'maintenance' in self.models:
                    features_scaled = self.scalers['maintenance'].transform(features)
                    maintenance_pred = self.models['maintenance'].predict(features_scaled)[0]
                    prediction.maintenance_probability = max(0, min(1, maintenance_pred))
                
                # Energy prediction
                if 'energy' in self.models:
                    features_scaled = self.scalers['energy'].transform(features)
                    energy_pred = self.models['energy'].predict(features_scaled)[0]
                    prediction.energy_forecast = max(0, energy_pred)
                
                # Update confidence based on model performance
                prediction.confidence = self._calculate_confidence(features)
            
            # Anomaly detection
            anomaly_score = self._detect_anomaly(features)
            if anomaly_score > 0.5:
                prediction.predicted_quality *= 0.8  # Reduce quality prediction for anomalies
                logger.warning(f"Anomaly detected for process {process_state.process_id}: score = {anomaly_score}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return Prediction(
                process_id=process_state.process_id,
                predicted_quality=50.0,
                predicted_cycle_time=120.0,
                predicted_defect_rate=10.0,
                maintenance_probability=0.5,
                energy_forecast=20.0,
                confidence=0.1,
                timestamp=time.time()
            )
    
    def train_models(self, training_data: List[Dict]):
        """Train ML models with collected data"""
        try:
            if len(training_data) < 50:
                logger.warning(f"Insufficient training data: {len(training_data)} samples")
                return False
            
            logger.info(f"Training models with {len(training_data)} samples")
            
            # Prepare training data
            X_quality, y_quality = [], []
            X_cycle, y_cycle = [], []
            X_maintenance, y_maintenance = [], []
            X_energy, y_energy = [], []
            
            for data in training_data:
                if 'features' in data and 'targets' in data:
                    features = data['features']
                    targets = data['targets']
                    
                    X_quality.append(features)
                    y_quality.append(targets.get('quality', 50.0))
                    
                    X_cycle.append(features)
                    y_cycle.append(targets.get('cycle_time', 120.0))
                    
                    X_maintenance.append(features)
                    y_maintenance.append(targets.get('maintenance_prob', 0.1))
                    
                    X_energy.append(features)
                    y_energy.append(targets.get('energy', 10.0))
            
            # Train models
            self._train_model('quality', np.array(X_quality), np.array(y_quality))
            self._train_model('cycle_time', np.array(X_cycle), np.array(y_cycle))
            self._train_model('maintenance', np.array(X_maintenance), np.array(y_maintenance))
            self._train_model('energy', np.array(X_energy), np.array(y_energy))
            
            # Train anomaly detector
            if len(X_quality) > 0:
                self.anomaly_detector.fit(X_quality)
            
            self.is_trained = True
            logger.info("ML models trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def _train_model(self, model_name: str, X: np.ndarray, y: np.ndarray):
        """Train individual model"""
        try:
            if len(X) == 0:
                return
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scalers[model_name].fit_transform(X_train)
            X_test_scaled = self.scalers[model_name].transform(X_test)
            
            # Train model
            self.models[model_name].fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.models[model_name].score(X_train_scaled, y_train)
            test_score = self.models[model_name].score(X_test_scaled, y_test)
            
            self.model_metrics[model_name] = {
                'train_score': train_score,
                'test_score': test_score,
                'samples': len(X)
            }
            
            logger.info(f"Model {model_name}: Train R² = {train_score:.3f}, Test R² = {test_score:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to train {model_name} model: {e}")
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence"""
        try:
            # Base confidence from model performance
            confidence = 0.5
            
            if self.is_trained and 'quality' in self.model_metrics:
                test_score = self.model_metrics['quality']['test_score']
                confidence = max(0.1, min(0.95, test_score))
            
            # Adjust confidence based on feature quality
            if len(features) > 0:
                feature_variance = np.var(features)
                if feature_variance < 0.1:  # Very low variance might indicate sensor issues
                    confidence *= 0.8
            
            return confidence
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _detect_anomaly(self, features: np.ndarray) -> float:
        """Detect anomalies in sensor data"""
        try:
            if hasattr(self.anomaly_detector, 'decision_function'):
                anomaly_score = self.anomaly_detector.decision_function(features)[0]
                # Convert to 0-1 scale (negative scores indicate anomalies)
                return max(0, min(1, -anomaly_score + 0.5))
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return 0.0

class DigitalTwinServer:
    """Main digital twin server coordinating all components"""
    
    def __init__(self):
        self.device_id = DEVICE_ID
        self.version = VERSION
        self.running = False
        
        # Initialize components
        self.physics_engine = PhysicsEngine()
        self.ml_engine = MLEngine()
        
        # Data storage
        self.sensor_buffer = deque(maxlen=MAX_DATA_BUFFER_SIZE)
        self.process_states = {}
        self.physics_states = {}
        self.predictions = {}
        
        # Communication
        self.serial_conn = None
        self.mqtt_client = None
        self.redis_client = None
        
        # Flask app for REST API
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Performance monitoring
        self.performance_metrics = {
            'sync_latency': deque(maxlen=100),
            'processing_time': deque(maxlen=100),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100)
        }
        
        # Setup API routes
        self._setup_api_routes()
        self._setup_websocket_handlers()
        
    def _setup_api_routes(self):
        """Setup REST API routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            return jsonify({
                'device_id': self.device_id,
                'version': self.version,
                'running': self.running,
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0,
                'sync_latency': np.mean(self.performance_metrics['sync_latency']) if self.performance_metrics['sync_latency'] else 0,
                'processes_active': len([p for p in self.process_states.values() if p.active]),
                'models_trained': self.ml_engine.is_trained
            })
        
        @self.app.route('/api/sensors/latest', methods=['GET'])
        def get_latest_sensors():
            if self.sensor_buffer:
                latest = self.sensor_buffer[-1]
                return jsonify(asdict(latest))
            return jsonify({'error': 'No sensor data available'}), 404
        
        @self.app.route('/api/processes', methods=['GET'])
        def get_processes():
            return jsonify([asdict(p) for p in self.process_states.values()])
        
        @self.app.route('/api/predictions', methods=['GET'])
        def get_predictions():
            return jsonify([asdict(p) for p in self.predictions.values()])
        
        @self.app.route('/api/physics/latest', methods=['GET'])
        def get_physics_state():
            if self.physics_states:
                # Convert numpy arrays to lists for JSON serialization
                latest_state = {}
                for key, state in self.physics_states.items():
                    latest_state[key] = {
                        'temperature_max': float(np.max(state.temperature_field)),
                        'temperature_min': float(np.min(state.temperature_field)),
                        'temperature_avg': float(np.mean(state.temperature_field)),
                        'stress_max': float(np.max(state.stress_field)),
                        'displacement_max': float(np.max(state.displacement_field)),
                        'material_properties': state.material_properties
                    }
                return jsonify(latest_state)
            return jsonify({'error': 'No physics data available'}), 404
        
        @self.app.route('/api/control/process/<process_id>', methods=['POST'])
        def control_process(process_id):
            data = request.get_json()
            command = data.get('command')
            
            if process_id in self.process_states:
                if command == 'start':
                    self.process_states[process_id].active = True
                    self._send_control_command({'command': 'start_process', 'process_id': process_id})
                elif command == 'stop':
                    self.process_states[process_id].active = False
                    self._send_control_command({'command': 'stop_process', 'process_id': process_id})
                elif command == 'set_parameters':
                    parameters = data.get('parameters', {})
                    self.process_states[process_id].parameters.update(parameters)
                    self._send_control_command({'command': 'set_parameters', 'process_id': process_id, 
                                              'parameters': parameters})
                
                return jsonify({'success': True})
            
            return jsonify({'error': 'Process not found'}), 404
        
        @self.app.route('/api/optimization/run', methods=['POST'])
        def run_optimization():
            try:
                result = self._run_process_optimization()
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/models/retrain', methods=['POST'])
        def retrain_models():
            try:
                # Collect training data from buffer
                training_data = self._prepare_training_data()
                success = self.ml_engine.train_models(training_data)
                return jsonify({'success': success, 'samples': len(training_data)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"WebSocket client connected: {request.sid}")
            emit('status', {'connected': True, 'device_id': self.device_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"WebSocket client disconnected: {request.sid}")
        
        @self.socketio.on('request_data')
        def handle_data_request(data):
            data_type = data.get('type', 'sensors')
            
            if data_type == 'sensors' and self.sensor_buffer:
                emit('sensor_data', asdict(self.sensor_buffer[-1]))
            elif data_type == 'processes':
                emit('process_data', [asdict(p) for p in self.process_states.values()])
            elif data_type == 'predictions':
                emit('prediction_data', [asdict(p) for p in self.predictions.values()])
    
    def start(self):
        """Start the digital twin server"""
        logger.info("Starting Digital Twin Edge Server...")
        self.start_time = time.time()
        self.running = True
        
        # Initialize connections
        self._initialize_serial()
        self._initialize_mqtt()
        self._initialize_redis()
        
        # Start background tasks
        threading.Thread(target=self._data_processing_loop, daemon=True).start()
        threading.Thread(target=self._physics_simulation_loop, daemon=True).start()
        threading.Thread(target=self._ml_inference_loop, daemon=True).start()
        threading.Thread(target=self._performance_monitoring_loop, daemon=True).start()
        
        logger.info("Digital Twin Edge Server started successfully")
        
        # Start Flask app
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=DEBUG)
    
    def stop(self):
        """Stop the digital twin server"""
        logger.info("Stopping Digital Twin Edge Server...")
        self.running = False
        
        if self.serial_conn:
            self.serial_conn.close()
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        if self.redis_client:
            self.redis_client.close()
    
    def _initialize_serial(self):
        """Initialize serial connection to Arduino"""
        try:
            self.serial_conn = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
            logger.info(f"Serial connection established: {SERIAL_PORT}")
        except Exception as e:
            logger.error(f"Failed to initialize serial connection: {e}")
            self.serial_conn = None
    
    def _initialize_mqtt(self):
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client(client_id=self.device_id)
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            logger.info("MQTT client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MQTT client: {e}")
            self.mqtt_client = None
    
    def _initialize_redis(self):
        """Initialize Redis client for caching"""
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            self.redis_client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
            self.redis_client = None
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            client.subscribe("digitaltwin/+/command")
            client.subscribe("digitaltwin/sensors/+")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            logger.debug(f"MQTT message received: {topic}")
            
            if 'command' in topic:
                self._handle_mqtt_command(payload)
            elif 'sensors' in topic:
                self._handle_external_sensor_data(payload)
                
        except Exception as e:
            logger.error(f"Failed to process MQTT message: {e}")
    
    def _handle_mqtt_command(self, payload):
        """Handle MQTT commands"""
        command = payload.get('command')
        
        if command == 'emergency_stop':
            logger.warning("Emergency stop command received via MQTT")
            self._send_control_command({'command': 'emergency_stop'})
        elif command == 'optimize_process':
            threading.Thread(target=self._run_process_optimization, daemon=True).start()
        elif command == 'retrain_models':
            threading.Thread(target=self._retrain_models, daemon=True).start()
    
    def _data_processing_loop(self):
        """Main data processing loop"""
        logger.info("Starting data processing loop")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Read sensor data from Arduino
                sensor_data = self._read_sensor_data()
                
                if sensor_data:
                    # Store in buffer
                    self.sensor_buffer.append(sensor_data)
                    
                    # Cache in Redis
                    if self.redis_client:
                        try:
                            self.redis_client.set('latest_sensor_data', 
                                                json.dumps(asdict(sensor_data)), 
                                                ex=300)  # 5 minute expiry
                        except Exception as e:
                            logger.warning(f"Failed to cache sensor data: {e}")
                    
                    # Broadcast to WebSocket clients
                    self.socketio.emit('sensor_data', asdict(sensor_data))
                    
                    # Update process states
                    self._update_process_states(sensor_data)
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000  # ms
                self.performance_metrics['processing_time'].append(processing_time)
                
                # Maintain target frequency (20 Hz)
                time.sleep(max(0, 0.05 - (time.time() - start_time)))
                
            except Exception as e:
                logger.error(f"Data processing loop error: {e}")
                time.sleep(1)
    
    def _physics_simulation_loop(self):
        """Physics simulation loop"""
        logger.info("Starting physics simulation loop")
        
        while self.running:
            try:
                start_time = time.time()
                
                if self.sensor_buffer:
                    latest_sensor_data = self.sensor_buffer[-1]
                    
                    # Update physics simulation for each active process
                    for process_id, process_state in self.process_states.items():
                        if process_state.active:
                            physics_state = self.physics_engine.update(latest_sensor_data, 0.1)
                            self.physics_states[process_id] = physics_state
                            
                            # Send physics feedback to Arduino
                            self._send_physics_feedback(process_id, physics_state)
                
                # Run simulation at 10 Hz
                time.sleep(max(0, 0.1 - (time.time() - start_time)))
                
            except Exception as e:
                logger.error(f"Physics simulation loop error: {e}")
                time.sleep(1)
    
    def _ml_inference_loop(self):
        """Machine learning inference loop"""
        logger.info("Starting ML inference loop")
        
        while self.running:
            try:
                start_time = time.time()
                
                if self.sensor_buffer:
                    latest_sensor_data = self.sensor_buffer[-1]
                    
                    # Run ML inference for each active process
                    for process_id, process_state in self.process_states.items():
                        if process_state.active:
                            prediction = self.ml_engine.predict(latest_sensor_data, process_state)
                            self.predictions[process_id] = prediction
                            
                            # Broadcast predictions
                            self.socketio.emit('prediction_update', asdict(prediction))
                            
                            # Send predictions to Arduino
                            self._send_prediction_update(process_id, prediction)
                
                # Run inference at 1 Hz
                time.sleep(max(0, 1.0 - (time.time() - start_time)))
                
            except Exception as e:
                logger.error(f"ML inference loop error: {e}")
                time.sleep(5)
    
    def _performance_monitoring_loop(self):
        """Performance monitoring loop"""
        logger.info("Starting performance monitoring loop")
        
        while self.running:
            try:
                # Monitor system performance
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                self.performance_metrics['cpu_usage'].append(cpu_percent)
                self.performance_metrics['memory_usage'].append(memory_info.percent)
                
                # Log performance metrics
                if len(self.performance_metrics['sync_latency']) > 0:
                    avg_latency = np.mean(self.performance_metrics['sync_latency'])
                    if avg_latency > SYNC_LATENCY_TARGET:
                        logger.warning(f"Sync latency above target: {avg_latency:.1f}ms")
                
                # Publish performance metrics
                if self.mqtt_client:
                    metrics = {
                        'device_id': self.device_id,
                        'timestamp': time.time(),
                        'cpu_usage': cpu_percent,
                        'memory_usage': memory_info.percent,
                        'sync_latency': np.mean(self.performance_metrics['sync_latency']) if self.performance_metrics['sync_latency'] else 0,
                        'active_processes': len([p for p in self.process_states.values() if p.active])
                    }
                    
                    self.mqtt_client.publish('digitaltwin/performance', json.dumps(metrics))
                
                time.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(10)
    
    def _read_sensor_data(self) -> Optional[SensorData]:
        """Read sensor data from Arduino"""
        try:
            if not self.serial_conn:
                return None
            
            sync_start = time.time()
            
            if self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8').strip()
                
                if line:
                    data = json.loads(line)
                    
                    # Calculate sync latency
                    sync_latency = (time.time() - sync_start) * 1000  # ms
                    self.performance_metrics['sync_latency'].append(sync_latency)
                    
                    # Parse sensor data
                    sensor_data = SensorData(
                        timestamp=data.get('timestamp', time.time() * 1000),
                        device_id=data.get('device_id', 'unknown'),
                        temperatures=data.get('temperatures', []),
                        pressures=data.get('pressures', []),
                        vibrations=data.get('vibration', {}).get('accelerations', []),
                        power=data.get('power', {}),
                        positions=data.get('positions', []),
                        forces=data.get('forces', []),
                        data_quality=data.get('data_quality', 1.0)
                    )
                    
                    return sensor_data
        
        except Exception as e:
            logger.error(f"Failed to read sensor data: {e}")
        
        return None
    
    def _update_process_states(self, sensor_data: SensorData):
        """Update process states based on sensor data"""
        try:
            # Initialize process states if needed
            if not self.process_states:
                self._initialize_process_states()
            
            # Update each process state
            for process_id, process_state in self.process_states.items():
                if process_state.active:
                    # Update cycle time
                    current_time = time.time()
                    if hasattr(process_state, 'start_time'):
                        process_state.cycle_time = current_time - process_state.start_time
                    
                    # Update efficiency
                    if process_state.cycle_time > 0:
                        process_state.efficiency = min(150.0, 
                            (process_state.target_cycle_time / process_state.cycle_time) * 100.0)
                    
                    # Update quality score based on sensor data
                    process_state.quality_score = self._calculate_quality_score(sensor_data, process_state)
        
        except Exception as e:
            logger.error(f"Failed to update process states: {e}")
    
    def _initialize_process_states(self):
        """Initialize default process states"""
        processes = [
            ('CNC_001', 'CNC_MACHINING', 180.0),
            ('3DP_001', '3D_PRINTING', 3600.0),
            ('INJ_001', 'INJECTION_MOLDING', 45.0),
            ('ASM_001', 'ASSEMBLY', 120.0)
        ]
        
        for process_id, process_type, target_time in processes:
            self.process_states[process_id] = ProcessState(
                process_id=process_id,
                process_type=process_type,
                active=False,
                cycle_time=0.0,
                target_cycle_time=target_time,
                efficiency=100.0,
                quality_score=95.0,
                parameters={}
            )
    
    def _calculate_quality_score(self, sensor_data: SensorData, process_state: ProcessState) -> float:
        """Calculate quality score based on sensor data and process type"""
        try:
            quality_score = 100.0
            
            # Temperature-based quality assessment
            if sensor_data.temperatures:
                temp_variation = np.std(sensor_data.temperatures)
                if temp_variation > 5.0:
                    quality_score -= min(20.0, temp_variation * 2)
            
            # Vibration-based quality assessment
            if sensor_data.vibrations:
                vibration_level = np.mean(np.abs(sensor_data.vibrations))
                if vibration_level > 2.0:
                    quality_score -= min(25.0, vibration_level * 5)
            
            # Pressure-based quality assessment
            if sensor_data.pressures:
                pressure_variation = np.std(sensor_data.pressures)
                if pressure_variation > 2.0:
                    quality_score -= min(15.0, pressure_variation * 3)
            
            # Process-specific quality factors
            if process_state.process_type == 'CNC_MACHINING':
                # Consider force stability and position accuracy
                if sensor_data.forces:
                    force_variation = np.std(sensor_data.forces)
                    if force_variation > 100.0:
                        quality_score -= min(20.0, force_variation / 10)
            
            elif process_state.process_type == 'INJECTION_MOLDING':
                # Consider pressure profile and cycle consistency
                if sensor_data.pressures and len(sensor_data.pressures) > 0:
                    if sensor_data.pressures[0] < 80.0 or sensor_data.pressures[0] > 120.0:
                        quality_score -= 25.0
            
            # Data quality factor
            quality_score *= sensor_data.data_quality
            
            return max(0.0, min(100.0, quality_score))
        
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 50.0
    
    def _send_control_command(self, command: Dict):
        """Send control command to Arduino"""
        try:
            if self.serial_conn:
                command_json = json.dumps(command)
                self.serial_conn.write((command_json + '\n').encode('utf-8'))
                logger.debug(f"Sent control command: {command}")
        except Exception as e:
            logger.error(f"Failed to send control command: {e}")
    
    def _send_physics_feedback(self, process_id: str, physics_state: PhysicsState):
        """Send physics simulation feedback to Arduino"""
        try:
            feedback = {
                'command': 'physics_feedback',
                'process_id': process_id,
                'max_temperature': float(np.max(physics_state.temperature_field)),
                'max_stress': float(np.max(physics_state.stress_field)),
                'max_displacement': float(np.max(physics_state.displacement_field)),
                'material_health': 1.0 - physics_state.material_properties.get('fatigue_damage', 0.0)
            }
            
            self._send_control_command(feedback)
        
        except Exception as e:
            logger.error(f"Failed to send physics feedback: {e}")
    
    def _send_prediction_update(self, process_id: str, prediction: Prediction):
        """Send prediction update to Arduino"""
        try:
            update = {
                'command': 'prediction_update',
                'process_id': process_id,
                'predicted_quality': prediction.predicted_quality,
                'predicted_cycle_time': prediction.predicted_cycle_time,
                'maintenance_probability': prediction.maintenance_probability,
                'confidence': prediction.confidence
            }
            
            self._send_control_command(update)
        
        except Exception as e:
            logger.error(f"Failed to send prediction update: {e}")
    
    def _run_process_optimization(self) -> Dict:
        """Run process optimization algorithm"""
        try:
            logger.info("Running process optimization...")
            
            optimization_results = {}
            
            for process_id, process_state in self.process_states.items():
                if process_state.active and process_id in self.predictions:
                    prediction = self.predictions[process_id]
                    
                    # Multi-objective optimization
                    # Objectives: maximize quality, minimize cycle time, minimize energy
                    def objective_function(params):
                        speed_factor, feed_factor = params
                        
                        # Simulate impact of parameter changes
                        simulated_quality = prediction.predicted_quality * (1 + 0.1 * (1 - speed_factor))
                        simulated_cycle_time = prediction.predicted_cycle_time * speed_factor
                        simulated_energy = prediction.energy_forecast * (speed_factor ** 1.5)
                        
                        # Weighted objective (minimize)
                        objective = (
                            -simulated_quality * 0.4 +  # Maximize quality
                            simulated_cycle_time * 0.3 +  # Minimize cycle time
                            simulated_energy * 0.3  # Minimize energy
                        )
                        
                        return objective
                    
                    # Optimization constraints
                    bounds = [(0.5, 1.5), (0.5, 1.5)]  # Speed and feed factor bounds
                    
                    # Run optimization
                    result = optimize.minimize(objective_function, [1.0, 1.0], bounds=bounds)
                    
                    if result.success:
                        optimal_speed, optimal_feed = result.x
                        
                        optimization_results[process_id] = {
                            'optimal_speed_factor': optimal_speed,
                            'optimal_feed_factor': optimal_feed,
                            'objective_value': result.fun,
                            'improvement_potential': prediction.predicted_quality * (1 + 0.1 * (1 - optimal_speed))
                        }
                        
                        # Send optimized parameters to Arduino
                        self._send_control_command({
                            'command': 'optimization_update',
                            'process_id': process_id,
                            'speed_factor': optimal_speed,
                            'feed_factor': optimal_feed
                        })
                        
                        logger.info(f"Optimization completed for {process_id}: speed={optimal_speed:.2f}, feed={optimal_feed:.2f}")
            
            return {
                'success': True,
                'optimized_processes': len(optimization_results),
                'results': optimization_results
            }
        
        except Exception as e:
            logger.error(f"Process optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_training_data(self) -> List[Dict]:
        """Prepare training data from sensor buffer"""
        training_data = []
        
        try:
            for i, sensor_data in enumerate(self.sensor_buffer):
                if i < len(self.sensor_buffer) - 1:  # Need next sample for targets
                    next_sensor_data = self.sensor_buffer[i + 1]
                    
                    # Find corresponding process state
                    for process_id, process_state in self.process_states.items():
                        if process_state.active:
                            features = self.ml_engine.extract_features(sensor_data, process_state).flatten()
                            
                            # Calculate targets from next sample
                            targets = {
                                'quality': process_state.quality_score,
                                'cycle_time': process_state.cycle_time,
                                'maintenance_prob': 0.1,  # Default value
                                'energy': sensor_data.power.get('active', 10.0)
                            }
                            
                            training_data.append({
                                'features': features.tolist(),
                                'targets': targets,
                                'process_id': process_id,
                                'timestamp': sensor_data.timestamp
                            })
        
        except Exception as e:
            logger.error(f"Failed to prepare training data: {e}")
        
        return training_data
    
    def _retrain_models(self):
        """Retrain ML models with latest data"""
        try:
            logger.info("Starting model retraining...")
            training_data = self._prepare_training_data()
            
            if len(training_data) >= 50:
                success = self.ml_engine.train_models(training_data)
                
                if success:
                    logger.info(f"Models retrained successfully with {len(training_data)} samples")
                    
                    # Publish retraining notification
                    if self.mqtt_client:
                        self.mqtt_client.publish('digitaltwin/models/retrained', 
                                               json.dumps({'success': True, 'samples': len(training_data)}))
                else:
                    logger.error("Model retraining failed")
            else:
                logger.warning(f"Insufficient training data: {len(training_data)} samples")
        
        except Exception as e:
            logger.error(f"Model retraining error: {e}")
    
    def _handle_external_sensor_data(self, data: Dict):
        """Handle sensor data from external sources"""
        try:
            # Convert external data to SensorData format
            sensor_data = SensorData(
                timestamp=data.get('timestamp', time.time() * 1000),
                device_id=data.get('device_id', 'external'),
                temperatures=data.get('temperatures', []),
                pressures=data.get('pressures', []),
                vibrations=data.get('vibrations', []),
                power=data.get('power', {}),
                positions=data.get('positions', []),
                forces=data.get('forces', []),
                data_quality=data.get('data_quality', 1.0)
            )
            
            # Add to buffer
            self.sensor_buffer.append(sensor_data)
            
            logger.debug(f"External sensor data received from {sensor_data.device_id}")
        
        except Exception as e:
            logger.error(f"Failed to handle external sensor data: {e}")

def main():
    """Main entry point"""
    server = DigitalTwinServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    main()