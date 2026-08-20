#!/bin/bash
# Seed Manifold Data (Person 1 -> Person 2 Handoff)
# Copies the generated JSON manifold frames from the AI Engine to the Backend

echo "Seeding backend with AI manifold frames..."

mkdir -p backend/data
cp -r ai_engine/data/manifold backend/data/

echo "✓ Successfully copied $(ls backend/data/manifold | grep .json | wc -l) files to backend/data/manifold/"
