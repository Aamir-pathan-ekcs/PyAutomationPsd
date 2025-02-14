import re
from psd_tools import PSDImage
from PIL import Image
import os
import numpy as np
from psd_tools.psd.engine_data import List
import math
from collections import Counter

input_dir = "input"
if not os.path.exists(input_dir):
    print(f"Input directory '{input_dir}' does not exist.")
    exit()
contactWrapAdded = False
for file_name in os.listdir(input_dir):
    file_path = os.path.join(input_dir, file_name)
    
    if os.path.isfile(file_path) and file_path.endswith(".psd"):
        try:
            psd = PSDImage.open(file_path)
            
            file_name_t = os.path.splitext(file_name)[0]
            width_meta, height_meta = psd.width, psd.height

            output_dir = f"output/{file_name_t}"
            os.makedirs(f"{output_dir}/images", exist_ok=True)
            os.makedirs(f"{output_dir}/css", exist_ok=True)

            def sanitize_filename(filename):
                """Sanitize layer names to be valid filenames."""
                return re.sub(r'[<>:"/\\|?*]', '_', filename)

            def get_better_color(layer):
                if layer.name == "cta" and layer.is_group() or layer.name == "contactWrap" and layer.is_group():
                    for rect in layer:
                        if rect.kind == "shape":
                            image = rect.topil()
                            pixels = list(image.getdata())
                            most_common_color = Counter(pixels).most_common(1)[0][0]
                            return most_common_color

            def get_layer_color(layer):
                if layer.name == "bg" or layer.name == "shape 1":
                    if layer.is_group():
                        return None 


                    if hasattr(layer, 'is_shape') and layer.is_shape():
                        try:
                            color = layer.fill_color
                            if color:
                                return color 
                        except AttributeError:
                            return None  

                    image = layer.composite()
                    image = image.convert("RGB")
                    np_image = np.array(image)

                    avg_color = np.mean(np_image, axis=(0, 1)) 
                    return tuple(map(int, avg_color))

                # if layer.name == "cta" and layer.is_group():
                #     print(f"checking layer {layer.name}")
                #     for rect in layer:
                #         print(f"checking insoide {rect.name}")
                #         if hasattr(rect, 'is_shape'):
                #             try:
                #                 color = rect.fill_color
                #                 if color:
                #                     return color 
                #             except AttributeError:
                #                 return None 

                #         image = rect.composite()
                #         image = image.convert("RGB")
                #         np_image = np.array(image) 

                #         avg_color = np.mean(np_image, axis=(0, 1))
                #         return tuple(map(int, avg_color))
            
            def get_text_layer_dimensions(layer):
                if layer.kind == 'type': 
                    tx1, ty1, tx2, ty2 = layer.bbox
                    width, height = tx2 - tx1, ty2 - ty1 
                    return width, height, tx1, ty1
                return None, None, None, None




            extracted_values = {}

            def process_layer(layer, html_content, css_content, content_html_app):

                image = layer.composite()
                sanitized_name = sanitize_filename(layer.name)
                    
                x1, y1, x2, y2 = layer.bbox
                width = x2 - x1
                height = y2 - y1
                global xe2, ye2, logo_width, logo_height, logo_x, logo_y
                checkHtmlContactWrap = checkAppendContactWrap = 1
                cnt = cnt2 = 0
                imageLayer = f"sd_img_Image"
                """Process individual layers and generate HTML/CSS."""
                if not layer.is_group() and layer.composite():
                    # If it's not a group and is a visible image layer, save it
                    # image = layer.composite()
                    # sanitized_name = sanitize_filename(layer.name)
                    
                    # # Extract bbox values (x1, y1, x2, y2)
                    # x1, y1, x2, y2 = layer.bbox
                    # width = x2 - x1
                    # height = y2 - y1

                    # if image:
                    #     sanitized_name = sanitize_filename(layer.name)
                    #     image_path = f"output/images/{sanitized_name}.png"
                    #     try:
                    #        image.save(image_path)
                    #        print(f"Saved image for {layer.name} at {image_path}")
                    #     except Exception as e:
                    #     print(f"Failed to save image for {layer.name}: {e}")

                    # if "Heading" in layer.name:
                    #     # For heading, add text and apply font styles
                    #     html_content.append(f'<div class="heading" id="{sanitized_name}" '
                    #                         f'style="position: absolute; left: {x1}px; top: {y1}px; '
                    #                         f'width: {width}px; height: {height}px; font-family: \'Lora\', serif; '
                    #                         f'font-size: 24px; color: #000;">')
                    #     html_content.append(f'{sanitized_name}')
                    #     html_content.append('</div>')

                    #     css_content.append(f"""
                    #         .heading {{
                    #             position: absolute;
                    #             left: {x1}px;
                    #             top: {y1}px;
                    #             width: {width}px;
                    #             height: {height}px;
                    #             font-family: 'Lora', serif;
                    #             font-size: 24px;
                    #             color: #000;
                    #         }}
                    #                     """)
                    
                    # if "Subheading" in layer.name:
                    #     # For subheading, add text and apply font styles
                    #     html_content.append(f'<div class="subheading" id="subheading-1" '
                    #                         f'style="position: absolute; left: {x1}px; top: {y1}px; '
                    #                         f'width: {width}px; height: {height}px; font-family: \'Ubuntu\', sans-serif; '
                    #                         f'font-size: 18px; color: #333;">')
                    #     html_content.append(f'{sanitized_name}')
                    #     html_content.append('</div>')

                    #     css_content.append(f"""
                    #         .subheading {{
                    #             position: absolute;
                    #             left: {x1}px;
                    #             top: {y1}px;
                    #             width: {width}px;
                    #             height: {height}px;
                    #             font-family: 'Ubuntu', sans-serif;
                    #             font-size: 18px;
                    #             color: #333;
                    #         }}
                    #                     """)
                    # global logo_width, logo_height, logo_x, logo_y
                    logo_processed = False
                    if "logoArea" in layer.name and not logo_processed:
                        logo_width, logo_height = width, height
                        logo_x, logo_y = x1, y1
                        return

                    if "logo" in layer.name:
                        image_path = f"output/{file_name_t}/images/{sanitized_name}.png"
                        if cnt == 0:
                            try:
                                image.save(image_path)
                                print(f"Saved image for {layer.name} at {image_path}")
                                extracted_values['logo_path'] = image_path
                            except Exception as e:
                                print(f"Failed to save image for {layer.name}: {e}")
                            html_content.append(f'<div class="logo">')
                            html_content.append(f'<img src="images/{sanitized_name}.png" alt="logo" id="sd_img_Logo"/>')
                            html_content.append('</div>')
                            css_content.append(f"""
                            .logo {{
                                width: {logo_width -3}px;
                                height: {logo_height - 3}px;
                                position: absolute;
                                left: {logo_x}px;
                                top: {logo_y}px;
                                display: flex;
                                align-items: flex-start;
                                justify-content: flex-start;
                            }}
                            .logo img{{
                                max-width: {logo_width -3}px;
                                max-height: {logo_height - 3}px;
                            }}
                            """)
                            logo_processed = True
                            print(f"Processed Logo: {sanitized_name}")

                    # elif "Hero" in layer.name:
                    #     html_content.append(f'<div class="mainImage1 imageBox" id="{imageLayer}">')
                    #     html_content.append(f'<img src="images/{sanitized_name}.png" alt="{sanitized_name}" id="sd_img_Image-1" />')
                    #     html_content.append('</div>')
                    #     sanitized_name = sanitize_filename(layer.name)
                    #     image_path = f"output/{file_name_t}/images/{sanitized_name}.png"
                    #     try:
                    #         image.save(image_path)
                    #         print(f"Saved image for {layer.name} at {image_path}")
                    #     except Exception as e:
                    #         print(f"Failed to save image for {layer.name}: {e}")
                    #     css_content.append(f"""
                    #         .imageBox {{
                    #             position: absolute;
                    #             left: {x1}px;
                    #             top: {y1}px;
                    #             width: {width}px;
                    #             height: {height}px;
                    #             z-index: 1;
                    #         }}
                    #         .imageBox img {{
                    #             width: {width}px;
                    #             height: {height}px;
                    #             object-fit: cover;
                    #         }}
                    #     """)
                    #     print(f"Processed image: {sanitized_name}")
                    
                    def extract_corner_points(layer):
                        """Extract corner points from a shape layer."""
                        if hasattr(layer, 'vector_mask') and layer.vector_mask:
                            vector_mask = layer.vector_mask
                            paths = vector_mask.paths
                            
                            if len(paths) > 0:
                                path = paths[0] 
                                points = []
                                
                                for knot in path:
                                    points.append(knot.anchor) 
                                
                                return points 
                        return None

                    def get_layer_effects(layer):
                        """Extract layer effects (like stroke) that could influence the border radius."""
                        if hasattr(layer, 'effects'):
                            effects = layer.effects
                            for effect in effects:
                                if effect.type == 'stroke':
                                    return effect
                        return None

                    def estimate_border_radius(corner_points, width, height, tolerance=5):
                        """Estimate the border radius based on the corner points with tolerance."""
                        if len(corner_points) != 4:
                            print("Error: Expected 4 corner points.")
                            return [0, 0, 0, 0]                        
                        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = corner_points

                        x1, y1 = x1 * width, y1 * height
                        x2, y2 = x2 * width, y2 * height
                        x3, y3 = x3 * width, y3 * height
                        x4, y4 = x4 * width, y4 * height
                        
                        print(f"Scaled Coordinates: TL({x1}, {y1}), TR({x2}, {y2}), BR({x3}, {y3}), BL({x4}, {y4})")
                        
                        top_edge = math.dist((x1, y1), (x2, y2))  
                        right_edge = math.dist((x2, y2), (x3, y3))  
                        bottom_edge = math.dist((x3, y3), (x4, y4)) 
                        left_edge = math.dist((x4, y4), (x1, y1)) 
                        
                        print(f"Edge lengths: top={top_edge}, right={right_edge}, bottom={bottom_edge}, left={left_edge}")
                        
                        if abs(top_edge - bottom_edge) < tolerance:
                            print("Rounded Rectangle Detected")
                            
                            top_bottom_radius = min(top_edge, bottom_edge)
                            return [0, 0, int(top_bottom_radius), int(top_bottom_radius)]
                        
                        print("No rounded corners detected.")
                        return [0, 0, 0, 0]
                    
                    if "shape 1" in layer.name:
                        
                        html_content.append(f'<div class="shape1 animate_fadeIn delay_0s" id="sd_bgcolor_Shape-1">')
                        html_content.append('</div>')
                        ShapeColor = get_layer_color(layer)

                        if layer.kind == "shape":
                            if hasattr(layer, "vector_mask") and layer.vector_mask:
                                vector_mask = layer.vector_mask
                                print(f"Vector Mask Found: {vector_mask}")

                        css_content.append(f"""
                        .shape1 {{
                            width: {width}px;
                            height: {height}px;
                            position: absolute;
                            left: {x1}px;
                            top: {y1}px;
                            background-color: rgb{ShapeColor};
                            border-radius: {0};
                           
                        }}
                                    """)

                    if "contentArea" in layer.name:
                        xe2, ye2 = x1, y1
                        css_content.append(f"""
                        .contentSection {{
                            width: {width}px;
                            height: {height}px;
                            position: relative;
                            left: {xe2}px;
                            top: {ye2}px;
                            overflow: hidden;
                        }}
                                    """)
                    # else:
                    #     xe2, ye2
                    # elif "imageHero1" in layer.name:
                    #     image_path = f"output/{file_name_t}/images/{sanitized_name}.png"
                    #     try:
                    #         image.save(image_path)
                    #         print(f"Saved image for {layer.name} at {image_path}")
                    #     except Exception as e:
                    #         print(f"Failed to save image for {layer.name}: {e}")
                    # elif "imageHero2" in layer.name:
                    #     image_path = f"output/{file_name_t}/images/{sanitized_name}.png"
                    #     try:
                    #         image.save(image_path)
                    #         print(f"Saved image for {layer.name} at {image_path}")
                    #     except Exception as e:
                    #         print(f"Failed to save image for {layer.name}: {e}")
                    # elif "imageHero3" in layer.name:
                    #     image_path = f"output/{file_name_t}/images/{sanitized_name}.png"
                    #     try:
                    #         image.save(image_path)
                    #         print(f"Saved image for {layer.name} at {image_path}")
                    #     except Exception as e:
                    #         print(f"Failed to save image for {layer.name}: {e}")        

                    print(f"Processed: {sanitized_name}")
                
                elif layer.is_group():
                    incre = cSubheading = 1
                    animateCr = 3
                    HeroAnimate = 0
                    animateCrOut = 6
                    counters = 1
                    print(f"Skipping group: {layer.name}")
                    for pp in reversed(layer):
                        # if layer.kind == "shape":
                        #     continue
                        if hasattr(pp, 'kind') and pp.kind == 'type':
                            print(f"Text layer found: {pp.name}")
                                                    # if pp.has_vector_mask():
                        #     print(f"mask {pp.name} has a vector mask")
                        #     vector_mask = pp.vector_mask()
                        #     print("Vector mask data:", vector_mask)
                        #     print(type(vector_mask))  # Debug: Check object type
                        #     print(dir(vector_mask)) 
                        #     if vector_mask and hasattr(vector_mask, "paths"):
                        #         print("Vector mask paths:", vector_mask.paths)
                            if hasattr(pp, 'text') and pp.text:
                                text_content = pp.text
                                print(f"Text content found: {text_content}")
                                if hasattr(pp, 'engine_dict'):
                                    engine_data = pp.engine_dict
                                    if hasattr(pp, 'transform'):
                                        transform_matrix = pp.transform
                                    try:
                                        if 'StyleRun' in engine_data:
                                            font_size = engine_data['StyleRun'].get('RunArray', [{}])[0].get('StyleSheet', {}).get('StyleSheetData', {}).get('FontSize', 'Font size not available')
                                            scaling_factor_x = transform_matrix[0]
                                            scaling_factor_y = transform_matrix[3]
                                            font_size_points = font_size
                                            dpi = 72
                                            font_size_pixels = font_size_points * (dpi / 72)
                                            scaled_font_size_x = font_size_pixels * scaling_factor_x
                                            scaled_font_size_y = font_size_pixels * scaling_factor_y
                                            empirical_factor = 0.75  
                                            effective_font_size = (scaled_font_size_x + scaled_font_size_y) / 2 * empirical_factor
                                            font_sized = f'{scaled_font_size_x:.2f}'
                                            # def get_photoshop_line_height(font_size, auto_leading=True, custom_ratio=1.2):
                                            #     font_size = float(font_size)
                                            #     ratio = 1.11 if auto_leading else custom_ratio
                                            #     line_height_px = round(font_size * ratio, 2)
                                            #     line_height_em = round(line_height_px / font_size, 2)
                                            #     return line_height_px, line_height_em

                                            # scaled_font_size_x2 = font_sized 
                                            # line_height_px, line_height_em = get_photoshop_line_height(scaled_font_size_x2)
                                            

                                            # print(engine_data['StyleRun'].get('RunArray', [{}])[0].get('StyleSheet', {}).get('StyleSheetData', {})).get("")
                                            # style = layer.engine_dict['StyleRun']['RunArray'][0]['StyleSheet']['StyleSheetData']
                                            # line_height = style.get('Leading', None)  # Extract line height

                                            # Extract Style Data
                                            LineHeightstyle_data = engine_data['StyleRun'].get('RunArray', [{}])[0].get('StyleSheet', {}).get('StyleSheetData', {})
                                            line_height = LineHeightstyle_data.get('Leading', None)
                                            try:
                                                line_height = float(line_height) if line_height and str(line_height).replace('.', '', 1).isdigit() else None
                                            except ValueError:
                                                line_height = None

                                            if line_height is None or line_height == 0:
                                                line_height = font_sized * 1.2 

                                            HScaling_factor_x = transform_matrix[0] if transform_matrix[0] != 0 else 1
                                            HScaling_factor_y = transform_matrix[3] if transform_matrix[3] != 0 else 1
                                            line_height_pixels = line_height * (dpi / 72)

                                            scaled_line_height_x = line_height_pixels * HScaling_factor_x
                                            scaled_line_height_y = line_height_pixels * HScaling_factor_y

                                            empirical_factor = 0.8 
                                            effective_line_height = (scaled_line_height_x + scaled_line_height_y) / 2 * empirical_factor

                                            line_height_em = effective_line_height / float(font_sized)
                                            # print(f"DEBUG: Font Size: {font_sized}, Raw Leading: {line_height}, "
                                            #     f"Scaled X: {scaled_line_height_x}, Scaled Y: {scaled_line_height_y}, Line Height EM: {line_height_em:.3f}")
                                            # print(f"Layer: {pp.name}, Line Height: {effective_line_height:.5f} px, {line_height_em:.3f} em")



                                        
                                        if 'StyleRun' in engine_data:
                                            # runlength = pp.engine_dict['StyleRun']['RunLengthArray']
                                            # caps = pp.engine_dict['StyleRun']['RunArray']
                                            # for index, style in enumerate(caps):
                                            #     font_caps = style['StyleSheet']['StyleSheetData'].get('FontCaps', None)
                                            #     print(f"FontCaps value for style {index}: {font_caps}")

                                            center = pp.engine_dict['StyleRun']
                                            font_caps = center.get('RunArray', [{}])[0].get('StyleSheet', {}).get('StyleSheetData', {}).get('FontCaps', None)
                                            style_run_alignment = center.get('RunArray', [{}])[0].get('StyleSheet', {}).get('StyleSheetData', {}).get('StyleRunAlignment', None)                                   
                                            paracheck = pp.engine_dict['ParagraphRun']
                                            aligncheck = paracheck.get('RunArray', [{}])[0].get('ParagraphSheet', {}).get('Properties', {}).get('Justification', None)
                                            if aligncheck == 0:
                                               text_align = "left"
                                            elif aligncheck == 1:
                                                text_align = "center"
                                            elif aligncheck == 2:
                                                text_align = "center"
                                            else:
                                                text_align = "left"

                                            if font_caps == 2:
                                                text_content = text_content.upper()  # Convert all text to uppercase
                                            # if font_caps == 1:
                                            #     text_content = "".join([char.upper() if char.islower() else char for char in text_content])
                                            else:
                                                text_content


                                            def rgba_to_rgb(rgba_values):
                                                if not rgba_values or len(rgba_values) < 3:
                                                    return None
                                                r = int(rgba_values[1] * 255)
                                                g = int(rgba_values[2] * 255)
                                                b = int(rgba_values[3] * 255)
                                                return (r, g, b)

                                            centers = pp.engine_dict.get('StyleRun', {})
                                            run_array = centers.get('RunArray', [{}])
                                            fill_color = run_array[0].get('StyleSheet', {}).get('StyleSheetData', {}).get('FillColor', {}).get('Values', None)
                                            stroke_color = run_array[0].get('StyleSheet', {}).get('StyleSheetData', {}).get('StrokeColor', {}).get('Values', None)
                                            if fill_color:
                                                rgb_fill = rgba_to_rgb(fill_color)

                                            if stroke_color:
                                                rgb_stroke = rgba_to_rgb(stroke_color)
                                            rgb_color = rgb_fill

                                            # fontset = pp.resource_dict['FontSet']
                                            def extract_font_weight(font_name):
                                                font_weights = {
                                                    'Thin': '100',
                                                    'ExtraLight': '200',
                                                    'Light': '300',
                                                    'Regular': '400',
                                                    'Normal': '400',
                                                    'Medium': '500',
                                                    'SemiBold': '600',
                                                    'Bold': '700',
                                                    'ExtraBold': '800',
                                                    'Black': '900',
                                                }

                                                font_name = font_name.strip().strip("'\"")
                                                font_name = font_name.replace("\xa0", " ")
                                                font_name = font_name.encode("ascii", "ignore").decode()
                                                
                                                match = re.match(r'^(.*?)[-_]?(Thin|ExtraLight|Light|Regular|Normal|Medium|SemiBold|Bold|ExtraBold|Black)?$', font_name, re.IGNORECASE)

                                                if match:
                                                    font_family = match.group(1)
                                                    fontWt = match.group(2) if match.group(2) else "Regular"
                                                else:
                                                    font_family = font_name
                                                    fontWt = "Regular"
                                                
                                                fontWt = fontWt.capitalize() if fontWt.lower() != "regular" else "Regular"
                                                fontGetWeight = font_weights.get(fontWt, '400')
                                                return font_family, fontWt, fontGetWeight

                                            fontset = pp.resource_dict['FontSet']
                                            fontsGet = str(fontset[0]['Name']).strip("'\"")
                                            
                                            family, font_weight_name, weight_value = extract_font_weight(fontsGet)

                                    except Exception as e:
                                        print(f"Error accessing engine dict data: {e}")
                                
                                else:
                                    print("Engine dict not available.")
                            
                        else:
                            print("This is not a text layer.")


                        # process_layer(pp, html_content, css_content)
                        sub_heading = f"sd_txta_Sub-Heading-{incre}"    
                        if "offer" in layer.name:
                            content_html_app.append(f'<div class="offerwrap animate_fadeIn delay_0s"><div class="offerBox" id="sd_txta_Offer-text">')
                            content_html_app.append(f'{text_content}')
                            content_html_app.append('</div></div>')

                            css_content.append(f"""
                            .offerBox {{
                                width: {width}px;
                                height: {height}px;
                                position: absolute;
                                left: {x1 - xe2}px;
                                top: {y1 - ye2}px;
                                font-family: '{family}', serif;
                                font-weight: {weight_value};
                                font-size: {font_sized}px;
                                color: rgb{rgb_color};
                                line-height: {line_height_em}em;
                                text-align: {text_align};
                            }}
                                        """)


                        if "contactWrap" in layer.name:
                            shapeWrap =  ' id="sd_bgcolor_Contact-Background"'
                            print(f"newww: {pp.name}")
                            if "contactBackground" in pp.name:
                                contentBgx1, contentBgy1, contentBgx2, contentBgy2 = pp.bbox
                                contentBgWidth = contentBgx2 - contentBgx1
                                contentBgHeight = contentBgy2 - contentBgy1    
                                print(f"bghh: {contentBgWidth}, {contentBgHeight}")
                                # html_content.append(f'<div class="outer contactWrap" id="sd_txta-BGGG">')
                                # html_content.append('</div>')
                                bgContact = get_better_color(layer)
                                css_content.append(f"""
                                    .contactWrap {{
                                            width: {contentBgWidth}px;
                                            height: {contentBgHeight}px;
                                            position: absolute;
                                            left: {contentBgx1}px;
                                            top: {contentBgy1}px;
                                            background: rgb{bgContact};
                                        }}
                                    """)
                            if "contactArea" in pp.name:
                                cx1, cy1, cx2, cy2 = pp.bbox
                                AreaConWidth = cx2 - cx1 -2
                                AreaConHeight = cy2 - cy1 -2

                            if "contactArea" not in getattr(pp, "name", "") and "contactBackground" not in getattr(pp, "name", ""):
                                if pp.kind == 'type':
                                    contactWidth, contactHeight, tx1, ty1 = get_text_layer_dimensions(pp)
                                if checkHtmlContactWrap == 1:
                                    classForContact = "tel"
                                    idContact = "Tel"
                                    content_html_app.append(f'<div class="contactWrap"{shapeWrap}>')
                                else:
                                    classForContact = "email"
                                    idContact = "Email"

                                content_html_app.append(f'<div class="{classForContact}" id="sd_txta-{idContact}">')
                                content_html_app.append(f'{text_content}')
                                content_html_app.append('</div>')
                                if checkHtmlContactWrap == 2:  
                                    content_html_app.append('</div>')  
                                checkHtmlContactWrap += 1 
                                
                                if checkAppendContactWrap == 1:    
                                    css_content.append(f"""
                                        .tel {{
                                            width: {AreaConWidth}px;
                                            height: {contactHeight}px;
                                            font-family: '{family}', serif;
                                            font-weight: {weight_value};
                                            font-size: {font_sized}px;
                                            color: rgb{rgb_color};
                                            line-height: {line_height_em}em;
                                            text-align: {text_align};
                                            position: absolute;
                                            left: {tx1 - xe2}px;
                                            top: {ty1 - xe2}px;
                                        }}

                                            """)
                                if checkAppendContactWrap == 2:            
                                    css_content.append(f"""
                                        .email {{
                                            width: {AreaConWidth}px;
                                            height: {contactHeight}px;
                                            font-family: '{family}', serif;
                                            font-weight: {weight_value};
                                            font-size: {font_sized}px;
                                            color: rgb{rgb_color};
                                            line-height: {line_height_em}em;
                                            text-align: {text_align};
                                            position: absolute;
                                            left: {tx1 - xe2}px;
                                            top: {ty1 - xe2}px;
                                        }}

                                            """)        
                                checkAppendContactWrap += 1
                                # if checkHtmlContactWrap > 1:
                            
                        
                        if "mainHeading" in layer.name:
                            content_html_app.append(f'<div class="textWrap animate_fadeOutRight delay_3s"><div class="mainHeading animate_fadeInLeft delay_0s" id="sd_txta_Heading">')
                            content_html_app.append(f'{text_content}')
                            content_html_app.append('</div></div>')
                            # headingColor = get_layer_color(layer)
                            css_content.append(f"""
                                .mainHeading {{
                                    width: {width}px;
                                    height: {height}px;
                                    position: absolute;
                                    left: {x1 - xe2}px;
                                    top: {y1 - ye2}px;
                                    font-family: '{family}', serif;
                                    font-weight: {weight_value};
                                    font-size: {font_sized}px;
                                    color: rgb{rgb_color};
                                    line-height: {line_height_em}em;
                                    text-align: {text_align};
                                }}
                                        """)
                        

                        if "subHeading" in layer.name:
                            if cSubheading == 1 or cSubheading == 2:
                                subHeadingAnimation = f" animate_fadeOut delay_{animateCrOut}_5s"
                            else:
                                subHeadingAnimation = ''
                            content_html_app.append(f'<div class="textWrap{subHeadingAnimation}"><div class="subHeading{incre} animate_fadeInLeft delay_{animateCr}_5s" id="{sub_heading}">')
                            content_html_app.append(f'{text_content}')
                            content_html_app.append('</div></div>')
                            if cSubheading == 1:
                                css_content.append(f"""
                                .subHeading1,.subHeading2,.subHeading3 {{
                                    width: {width}px;
                                    height: {height}px;
                                    position: absolute;
                                    left: {x1 - xe2}px;
                                    top: {y1 - ye2}px;
                                    font-family: '{family}', serif;
                                    font-weight: {weight_value};
                                    font-size: {font_sized}px;
                                    color: rgb{rgb_color};
                                    line-height: {line_height_em}em;
                                    text-align: {text_align};
                                }}
                                        """)
                            incre += 1; cSubheading += 1
                            animateCr += 4; animateCrOut += 3
                        if "hero" in layer.name or "hero2" in layer.name:
                            print(f"Processing hero layer: {layer.name}")
                            cssImage = None
                            check = None
                            for idx, child_layer in enumerate(reversed(layer)):
                                if "imageWrap1" in child_layer.name or "imageWrap" in child_layer.name:
                                    print(f"skipping shape: {child_layer.name}")
                                    # if child_layer.kind == "shape":
                                    #     print("yyyyyy")
                                    #     if hasattr(child_layer, "vector_mask") and child_layer.vector_mask:
                                    #         vector_mask = child_layer.vector_mask
                                    #         print(f"Vector Mask Found: {vector_mask}")

                                    #         # Extract paths
                                    #         for path_idx, path in enumerate(vector_mask.paths):
                                    #             print(f"Processing Path {path_idx + 1}:")
                                                
                                    #             clip_path_points = []
                                                
                                    #             for point in path:
                                    #                 if hasattr(point, "anchor"):  # Extract anchor points
                                    #                     x, y = point.anchor
                                    #                     clip_path_points.append((x, y))
                                    #                     print(f"  Point: ({x}, {y})")

                                    #             # Convert points to CSS `clip-path: polygon(...)` format
                                    #             if clip_path_points:
                                    #                 clip_path_css = "clip-path: polygon(" + ", ".join(f"{x*100}% {y*100}%" for x, y in clip_path_points) + ");"
                                    #                 print(f"Generated Clip Path: {clip_path_css}")


                                    check = child_layer.name
                                    x1, y1, x2, y2 = child_layer.bbox
                                    width = x2 - x1
                                    height = y2 - y1
                                    print(f"{child_layer.name} bbox have this{x1, y1, x2, y2}")
                                    continue
                                if pp.kind not in ['pixel', 'smartobject']:
                                    print(f"no pixel")
                                    continue
                                if pp.is_visible():
                                    image_path = f"output/{file_name_t}/images/{child_layer.name}.png"
                                    imageFileName = child_layer.name
                                    try:
                                        layer_image = child_layer.topil()
                                        cropped_image = layer_image.crop()
                                        cropped_image = cropped_image.crop(cropped_image.getbbox())
                                        cropped_image.save(image_path)
                                    except:
                                        print(f"Failed to save image for {pp.name}: {e}")                    
                            if counters == 1 or counters == 2 or counters == 3:
                                HeroAnimation = f" animate_fadeIn delay_{HeroAnimate}_5s"
                            else:
                                HeroAnimation = ''              
                            if "hero" in layer.name: 
                                cssImage = 1
                                if "imageWrap1" not in pp.name and "imageWrap" not in pp.name:  
                                    html_content.append(f'<div class="mainImage{counters} imageBox{cssImage} {HeroAnimation}">')
                                    html_content.append(f'<img src="images/{pp.name}.png" alt="{sanitized_name}" id="{imageLayer}-{counters}" />')
                                    html_content.append('</div>')
                                counters += 1
                            if "hero2" in layer.name: 
                                cssImage = 2  
                                if "imageWrap1" not in pp.name and "imageWrap" not in pp.name:  
                                    html_content.append(f'<div class="mainImage{counters} imageBox{cssImage} {HeroAnimation}">')
                                    html_content.append(f'<img src="images/{pp.name}.png" alt="{sanitized_name}" id="{imageLayer}-{counters}" />')
                                    html_content.append('</div>')
                                counters += 1      
                            if counters == 1 or counters == 3:
                                css_content.append(f"""
                                    .imageBox{cssImage} {{
                                        width: {width-3}px;
                                        height: {height-3}px;
                                        position: absolute;
                                        left: {x1}px;
                                        top: {y1}px;
                                        z-index: 1;
                                    }}
                                    .imageBox{cssImage} img {{
                                        width: {width-3}px;
                                        height: {height-3}px;
                                        object-fit: cover;
                                    }}
                                """)
                            HeroAnimate += 4    
                            print(f"Processed image: {sanitized_name}")


                        # if "hero2" in layer.name:
                        #     print(f"from hero 2: {pp.name}")
                        #     for idx, child_layer in enumerate(reversed(layer)):
                        #         if "imageWrap1" in child_layer.name or "imageWrap" in child_layer.name:
                        #             print(f"skipping shape: {child_layer.name}")
                        #             x1, y1, x2, y2 = child_layer.bbox
                        #             width = x2 - x1
                        #             height = y2 - y1
                        #             print(f"{child_layer.name} bbox have this{x1, y1, x2, y2}")
                        #             continue
                        #         if pp.kind not in ['pixel', 'smartobject']:
                        #             print(f"no pixel")
                        #             continue
                        #         if pp.is_visible():
                        #             image_path = f"output/{file_name_t}/images/{child_layer.name}.png"
                        #             imageFileName = child_layer.name
                        #             try:
                        #                 layer_image = child_layer.topil()
                        #                 cropped_image = layer_image.crop()
                        #                 cropped_image = cropped_image.crop(cropped_image.getbbox())
                        #                 cropped_image.save(image_path)
                        #             except:
                        #                 print(f"Failed to save image for {pp.name}: {e}")      
                        #     if not "imageWrap1" in pp.name:
                        #         print(f"pppp{idx}")
                        #         cnt2 += 1  
                        #         html_content.append(f'<div class="mainImage{cnt2} imageBox2 animate_zoomInZoomOut delay_0s">')
                        #         html_content.append(f'<img src="images/{pp.name}.png" alt="{sanitized_name}" id="{imageLayer}-{cnt2}-second" />')
                        #         html_content.append('</div>')
                        #         if cnt2 == 1:
                        #             css_content.append(f"""
                        #                 .imageBox2 {{
                        #                     width: {width-3}px;
                        #                     height: {height-3}px;
                        #                     position: absolute;
                        #                     left: {x1}px;
                        #                     top: {y1}px;
                        #                     z-index: 1;
                        #                 }}
                        #                 .imageBox2 img {{
                        #                     width: {width-3}px;
                        #                     height: {height-3}px;
                        #                     object-fit: cover;
                        #                 }}
                        #             """)
                        #         print(f"Processed image: {sanitized_name}")

                                       
                        if "cta" in pp.name:
                            def calculate_distance(p1, p2, width, height):
                                x1, y1 = p1[0] * width, p1[1] * height
                                x2, y2 = p2[0] * width, p2[1] * height
                                return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                            canvas_width, canvas_height = psd.width, psd.height
                            if pp.has_vector_mask():
                                vector_paths = pp.vector_mask.paths
                                points = [point.anchor for path in vector_paths for point in path]

                                if len(points) >= 4: 
                                    radius_p = calculate_distance(points[0], points[1], canvas_width, canvas_height)
                                    # print(f"Calculated distance: {radius_p}")
                                    if radius_p <= 0:
                                        radius = radius_p / float(font_sized)
                                        radius_e = radius
                                        print(f"Layer '{pp.name}' has a border radius of {radius_e:.2f} pixels")
                                    else:
                                        radius_e = 0
                                        print(f"Layer '{pp.name}' is a sharp-edged rectangle (no border radius).")

                                    # print(f"Estimated border radius: {radius_e:.2f} pixels")
                                else:
                                    radius_e = 0
                                    # print("Not enough points detected for a rounded rectangle.")


                            content_html_app.append(f'<div class="cta animate_fadeIn delay_4_5s">')
                            content_html_app.append(f'<a class="button" id="sd_btn_Click-Through-URL" target="_blank" href="http://www.ekcs.co">{text_content}')
                            content_html_app.append('</a>')
                            content_html_app.append('</div>')
                            ctaColor = get_better_color(layer)
                            css_content.append(f"""
                                .cta {{
                                    position: absolute;
                                    left: {x1 - xe2}px;
                                    top: {y1 - ye2}px;
                                    text-align: center;
                                }}
                                .button {{
                                    min-width: {width}px;
                                    max-width: {width + 2}px;
                                    max-height: {height -2}px;
                                    font-size: {font_sized}px;
                                    font-family: '{family}', serif;
                                    font-weight: {weight_value};
                                    font-style: normal;
                                    cursor: pointer; 
                                    color: rgb{rgb_color};
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    background-color: rgb{ctaColor};
                                    padding: 0.5em 0.65em 0.51em;
                                    text-align: center;
                                    line-height: {line_height_em}em;
                                    border-radius: {radius_e}em;
                                }}
                            """)
                        
                        # if "contactWrap" in layer.name:
                        #     if "contactArea" in pp.name or 'contactBackground' in pp:
                        #         continue
                        #     content_html_app.append(f'<div class="contactWrap animate_fadeIn delay_0s"><div class="contactText" id="sd_txta-text">')
                        #     content_html_app.append(f'{text_content}')
                        #     content_html_app.append('</div></div>')
                        #     print(f"gettting {pp}")
                        #     if pp.kind == 'type':
                        #         wws, hhs = get_text_layer_dimensions(pp)
                        #         print(f"sTexts: {pp} Width: {wws}px, Height: {hhs}px")
                        #     css_content.append(f"""
                        #     .contactWrap {{
                        #         width: {width}px;
                        #         height: {height}px;
                        #         position: absolute;
                        #         left: {x1 - xe2}px;
                        #         top: {y1 - ye2}px;
                        #         font-family: {fontf}', serif;
                        #         font-weight: {fontGetWeight};
                        #         font-size: {font_sized}px;
                        #         color: rgb{rgb_color};
                        #         line-height: {line_height_em}em;
                        #         text-align: {text_align};
                        #     }}

                        #                 """)

                        # if hasattr(pp, 'layers') and pp.layers:
                        #     process_layer(pp, html_content, css_content)
                    # for child_layer in layer:
                    #     process_layer(child_layer, html_content, css_content)
                        
                    #     if hasattr(child_layer, 'text') and child_layer.text:
                    #         text_content = child_layer.text
                    #         print(f"Text content found: {text_content}")
                else:
                    print(f"Skipping unsupported layer: {layer.name}")


            for layer in psd:
                if layer.name == "bg":
                    color = get_layer_color(layer)
                    if color:
                        print(f"backgroundColor has color: {color}")
                    else:
                        print("backgroundColor has no color.") 


                html_content = ['<!DOCTYPE html>',
                                '<html lang="en">',
                                '<head>',
                                '<meta charset="UTF-8" />',
                                '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
                                f'<meta name="ad.size" content="width={width_meta},height={height_meta}" />',
                                '<meta http-equiv="X-UA-Compatible" content="ie=edge" />',
                                f'<title>{file_name_t}</title>',
                                '<link rel="preconnect" href="https://fonts.googleapis.com" />',
                                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
                                f'<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">',
                                '<link rel="stylesheet" href="https://digital.mediaferry.com/animation.css">',
                                '<link rel="stylesheet" href="./css/style.css" />',
                                '</head>',
                                '<body>',
                                '<div class="container" id="sd_bgcolor_Main-Background">',
                                '<a href="javascript:window.open(window.trackingUrl + window.clickTag)"></a>',
                                '<a class="clicktru" target="_blank" href="#"></a>',
                                # '<div class="contentSection">'
                        ]
                content_html_app = []
                css_content = [
                    '''* {
                        margin: 0px;
                        padding: 0px;
                        box-sizing: border-box;
                    }''',
                    '''
                    :root {
                        --width: %(width_meta)spx;
                        --height: %(height_meta)spx;
                    }
                    '''% {"width_meta": width_meta, "height_meta": height_meta},
                    '''
                    .container {
                        width: %(width_meta)spx;
                        height: %(height_meta)spx;
                        position: relative;
                        overflow: hidden;
                        border: 1px solid #7a8599;
                        background-color: rgb%(color)s;
                    }
                    '''% {"width_meta": width_meta, "height_meta": height_meta, "color": color},
                    '''   .clicktru {
                        z-index:9999; width:100%; height:100%; position:absolute;
                    }''',
                    '''
                        a{
                            text-decoration:none;
                    } ''',
                    '''
                        #sd_btn_Click-Through-URL:empty{display:none;} 
                    '''
                    ]

                for layer in psd:
                    process_layer(layer, html_content, css_content, content_html_app)

                html_content.append('<div class="contentSection">')
                html_content.extend(content_html_app)
                html_content.append('</div>')

                html_content.append('''
                    </div>
                    <script>
                        function getQueryStringValue(key) {
                            return decodeURIComponent(window.location.search.replace(new RegExp("^(?:.*[&\\?]" + escape(key).replace(/[\\.\\+\\*]/g, "\\\\$&") + "(?:\\=([^&]*))?)?.*$", "i"), "$1"));
                        }

                        var clickTag = document.getElementById("sd_btn_Click-Through-URL").getAttribute("href");
                        var trackingUrl = getQueryStringValue("trackurl");
                        var resURL = trackingUrl + clickTag;

                        var elements = document.getElementsByClassName("clicktru");

                        for (var i = 0; i < elements.length; i++) {
                            elements[i].setAttribute("href", resURL);
                        }
                    </script>
                </body>
                </html>
                ''')
    

                with open(f'{output_dir}/index.html', 'w') as f:
                    f.write("\n".join(html_content))

                with open(f'{output_dir}/css/style.css', 'w') as f:
                    f.write("\n".join(css_content))

                print("HTML and CSS files generated.")

        except Exception as e:
            print(f"Error processing file '{file_name}': {e}")    
