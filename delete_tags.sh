#!/bin/bash

REMOTE=origin

for i in $(seq 101 102); do
  TAG="1.0.$i"
  # Delete local tag if exists (ignore errors)
  git tag -d "$TAG" 2>/dev/null
  # Delete remote tag (ignore errors)
  git push "$REMOTE" --delete "$TAG" 2>/dev/null || true
done

