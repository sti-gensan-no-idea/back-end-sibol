# app/services/ar_service.py
from fastapi import HTTPException
from app.config.settings import settings
import json

class ARService:
    @staticmethod
    def generate_ar_scene_config(property_details: dict):
        try:
            scene_config = {
                "model_url": f"{settings.AR_MODEL_STORAGE_URL}/{property_details['id']}/model.glb",
                "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "lighting": {
                    "ambient": {"intensity": 0.5},
                    "directional": {"intensity": 0.8, "position": {"x": 10, "y": 10, "z": 10}}
                },
                "environment": {
                    "floor": {"texture": "default", "reflectivity": 0.2},
                    "skybox": "default"
                },
                "property_metadata": {
                    "title": property_details["title"],
                    "type": property_details["type"],
                    "location": property_details["location"]
                }
            }
            return json.dumps(scene_config)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AR scene generation failed: {str(e)}")