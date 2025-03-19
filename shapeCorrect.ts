def create_shapes(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Smooth image
        edges = cv2.Canny(gray, 30, 100)  # Adjusted for better edge detection
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)  # Connect broken edges
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for i, contour in enumerate(contours, 1):
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if area < 1000:  # Adjusted threshold for large shapes
                continue

            # Dynamic epsilon for large contours
            epsilon = 0.01 * perimeter if perimeter > 1000 else 0.03 * perimeter
            approx = cv2.approxPolyDP(contour, epsilon, True)
            sides = len(approx)

            print(f"Contour {i}: Area={area}, Perimeter={perimeter}, Sides={sides}")

            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (center, axes, angle) = ellipse
                aspect_ratio = axes[0] / axes[1] if axes[1] != 0 else 1
                
                if sides == 3:
                    shape = "Triangle"
                    clip_path = "polygon(" + ", ".join(f"{p[0][0]}px {p[0][1]}px" for p in approx) + ")"
                elif sides == 4:
                    shape = "Rectangle"
                    clip_path = "polygon(" + ", ".join(f"{p[0][0]}px {p[0][1]}px" for p in approx) + ")"
                elif sides > 8 and 0.95 <= aspect_ratio <= 1.05:
                    shape = "Circle"
                    clip_path = f"circle({axes[0]/2:.1f}px at {center[0]:.1f}px {center[1]:.1f}px)"
                elif sides > 6 and (aspect_ratio < 0.95 or aspect_ratio > 1.05):
                    shape = "Ellipse"
                    num_points = 128 
                    ellipse_points = []
                    angle_rad = math.radians(angle)
                    cos_angle = math.cos(angle_rad)
                    sin_angle = math.sin(angle_rad)
                    a, b = axes[0] / 2, axes[1] / 2
                    cx, cy = center

                    for t in range(num_points):
                        theta = 2 * math.pi * t / num_points
                        x = cx + a * math.cos(theta) * cos_angle - b * math.sin(theta) * sin_angle
                        y = cy + a * math.cos(theta) * sin_angle + b * math.sin(theta) * cos_angle
                        ellipse_points.append(f"{x:.2f}px {y:.2f}px")
                    
                    clip_path = "polygon(" + ", ".join(ellipse_points) + ")"
                else:
                    shape = f"Polygon with {sides} sides"
                    clip_path = "polygon(" + ", ".join(f"{p[0][0]}px {p[0][1]}px" for p in approx) + ")"
            else:
                shape = f"Polygon with {sides} sides"
                clip_path = "polygon(" + ", ".join(f"{p[0][0]}px {p[0][1]}px" for p in approx) + ")"

            print(f"Processed: Shape {i} - {shape}")
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)
            if 'ellipse' in locals():
                cv2.ellipse(image, ellipse, (255, 0, 0), 2)

        # Save output for debugging ssss done
        cv2.imwrite("output.jpg", image)
        os.remove(image_path)
        return clip_path
    except Exception as e:
        print(f"Error in create_shapes for {image_path}: {e}")
        return None
