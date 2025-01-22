import re
from psd_tools import PSDImage
from PIL import Image
import os
import numpy as np
from psd_tools.psd.engine_data import List


input = "input"

file_path = f"./{input}/Testing_OfferLed4_160x600.psd"
psd = PSDImage.open(file_path)

base_name = os.path.basename(file_path)
file_name_t = os.path.splitext(base_name)[0]
width_meta, height_meta = psd.width, psd.height

os.makedirs(f"output/{file_name_t}/images", exist_ok=True)
os.makedirs(f"output/{file_name_t}/css", exist_ok=True)
os.makedirs("output", exist_ok=True)

def sanitize_filename(filename):
    """Sanitize layer names to be valid filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def get_layer_color(layer):
    if layer.name == "backgroundColor":
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
    if layer.name == "shape 1":
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

    if layer.name == "cta":
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

    if layer.name == "offer":
        for poi in layer:
            if hasattr(poi, 'text'):
                try:
                    if hasattr(poi.text, 'fill_color'):
                        color = poi.text.fill_color
                        print("Text fill color:", color)
                        if color:
                            if len(color) == 4: 
                                r, g, b, a = color
                                if a < 1:
                                    print("Detected transparency, using RGB color")
                                    return (r, g, b)
                                else:
                                    return (r, g, b, a) 

                    elif hasattr(poi.text, 'font_color'):
                        color = poi.text.font_color
                        print("Text font color:", color)
                        if color:
                            return color 

                except AttributeError:
                    print("No color attribute found in text.")
                    return None
            
            image = poi.composite()
            image = image.convert("RGB") 
            np_image = np.array(image)
            avg_color = np.mean(np_image, axis=(0, 1))
            return tuple(map(int, avg_color))  

        return None


extracted_values = {}

def process_layer(layer, html_content, css_content):

    image = layer.composite()
    sanitized_name = sanitize_filename(layer.name)
        
    x1, y1, x2, y2 = layer.bbox
    width = x2 - x1
    height = y2 - y1
    cnt = 0
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
        if "logo" in layer.name:
            image_path = f"output/{file_name_t}/images/{sanitized_name}.png"
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
                position: absolute;
                left: {x1}px;
                top: {y1}px;
                width: {width}px;
                height: {height}px;
                background-color: #d3d3d3;
            }}
            .logo img{{
                max-width: {width}px;
                max-height: {height}px;
            }}
            """)
            print(f"Processed Logo: {sanitized_name}")
         

        elif "cta" in layer.name:
            html_content.append(f'<div class="cta">')
            html_content.append(f'<a class="button" id="sd_btn_Click-Through-URL" target="_blank" href="http://www.ekcs.co">{sanitized_name}')
            html_content.append('</a>')
            html_content.append('</div>')
            ctaColor = get_layer_color(layer)
            css_content.append(f"""
                .cta {{
                    width: {width}px;
                    height: {height}px;
                    position: absolute;
                    left: {x1}px;
                    top: {y1}px;
                    font-size: 16px;
                    color: #fff;
                    background-color: rgb{ctaColor};
                    padding: 0.75em 0.75em 0.75em;
                    text-align: center;
                }}
                            """)

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
        

        
        elif "shape 1" in layer.name:
            
            html_content.append(f'<div class="shape1" id="sd_bgcolor_Shape-1">')
            html_content.append('</div>')
            ShapeColor = get_layer_color(layer)
            css_content.append(f"""
            .shape1 {{
                width: {width}px;
                height: {height}px;
                position: absolute;
                left: {x1}px;
                top: {y1}px;
                background-color: rgb{ShapeColor};
            }}
                        """)

        
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
        incre = 1
        print(f"Skipping group: {layer.name}")
        for pp in reversed(layer):
            if hasattr(pp, 'kind') and pp.kind == 'type':
                print(f"Text layer found: {pp.name}")
                
                if hasattr(pp, 'text') and pp.text:
                    text_content = pp.text
                    print(f"Text content found: {text_content}")
                    
                    if hasattr(pp, 'engine_dict'):
                        engine_data = pp.engine_dict
                        # if hasattr(pp, 'transform'):
                      	#     transform_matrix = pp.transform
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

                            if 'StyleRun' in engine_data:
                                run_array = engine_data['StyleRun'].get('RunArray', [])
                                # print(f"RunArray: {run_array}")

                                if run_array:
                                    stylesheet = run_array[0].get('StyleSheet', {})
                                    # print(f"Stylesheet: {stylesheet}")

                                    stylesheet_data = stylesheet.get('StyleSheetData', {})
                                    # print(f"StyleSheetData: {stylesheet_data}")

                                    fill_color = stylesheet_data.get('FillColor', {}).get('Values', None)
                                    # print(f"Raw FillColor: {fill_color}")

                                    if isinstance(fill_color, List):
                                        fill_color = list(fill_color)
                                        print(f"Converted FillColor to Python list: {fill_color}")


                                    if isinstance(fill_color, list):
                                        if len(fill_color) == 4:
                                            try:
                                                fill_color = [float(c) for c in fill_color]
                                                print("Converted FillColor elements to float.")

                                                r = int(fill_color[0] * 255)
                                                g = int(fill_color[1] * 255)
                                                b = int(fill_color[2] * 255)
                                                a = fill_color[3]  # Alpha value

                                                if a < 0.1: 
                                                    a = 0.1
                                                    print("Alpha value is too low. Adjusted to minimum threshold of 0.1.")

                                                if a < 1.0:
                                                    color = f"rgba({r}, {g}, {b}, {a:.2f})"
                                                else:
                                                    color = f"rgb({r}, {g}, {b})"
                                                
                                                print(f"Final Text color: {color}")
                                            except (ValueError, TypeError) as e:
                                                print(f"Error processing FillColor values: {e}")
                                        else:
                                            print(f"FillColor does not have exactly 4 elements: {fill_color}")
                                    else:
                                        print(f"FillColor is not a valid list. Type: {type(fill_color)}")
                                else:
                                    print("RunArray is empty or improperly structured.")
                            else:
                                print("StyleRun not found in engine_data.")



                            if 'StyleRun' in engine_data:
                                font_family = engine_data['StyleRun'].get('RunArray', [{}])[0].get('StyleSheet', {}).get('StyleSheetData', {}).get('Font', 'Font family not available')
                                print(f"Font family found in engine dict: {font_family}")
                        except Exception as e:
                            print(f"Error accessing engine dict data: {e}")
                    
                    else:
                        print("Engine dict not available.")
                
            else:
                print("This is not a text layer.")


            process_layer(pp, html_content, css_content)
            sub_heading = f"sd_txta_Sub-Heading-{incre}"    
            if "offer" in layer.name:
                html_content.append(f'<div class="offerwrap"><div class="offerBox" id="sd_txta_Offer-text">')
                html_content.append(f'{text_content}')
                html_content.append('</div></div>')
                offerColor = get_layer_color(layer)
                css_content.append(f"""
                .offerBox {{
                    width: {width}px;
                    height: {height}px;
                    position: absolute;
                    left: {x1}px;
                    top: {y1}px;
                    font-family: '{font_family}', serif;
                    font-size: {font_sized}px;
                    color: rgba{offerColor};
                }}
                            """)

            
            if "mainHeading" in layer.name:
                html_content.append(f'<div class="textWrap"><div class="mainHeading" id="sd_txta_Heading">')
                html_content.append(f'{text_content}')
                html_content.append('</div></div>')

                css_content.append(f"""
                .mainHeading {{
                    width: {width}px;
                    height: {height}px;
                    position: absolute;
                    left: {x1}px;
                    top: {y1}px;
                    font-family: '{font_family}', serif;
                    font-size: {font_sized}px;
                    color: rgba({color});
                }}
                            """)

            if "subHeading" in layer.name:

                html_content.append(f'<div class="textWrap"><div class="subHeading{incre}" id="{sub_heading}">')
                html_content.append(f'{text_content}')
                html_content.append('</div></div>')

                css_content.append(f"""
                    .subHeading{incre} {{
                        width: {width}px;
                        height: {height}px;
                        position: absolute;
                        left: {x1}px;
                        top: {y1}px;
                        font-family: '{font_family}', serif;
                        font-size: {font_sized}px;
                        color: rgba({color});
                    }}
                            """)
                incre += 1 
            
            if "hero" in layer.name:
                print(f"from hero: {pp.name}")
                for index, child_layer in enumerate(layer):
                    if index == 0:
                        x1, y1, x2, y2 = child_layer.bbox
                        width = x2 - x1
                        height = y2 - y1
                        cnt += 1
                        print(f"Processing first child layer: {child_layer.name} {width} {height}")
                        image_path = f"output/{file_name_t}/images/{pp.name}.png"
                        try:
                            image.save(image_path)
                            print(f"Saved image for {pp.name} at {image_path}")
                        except Exception as e:
                            print(f"Failed to save image for {layer.name}: {e}")
                html_content.append(f'<div class="mainImage{cnt} imageBox">')
                html_content.append(f'<img src="images/{pp.name}.png" alt="{sanitized_name}" id="{imageLayer}-{cnt}" />')
                html_content.append('</div>')
                layer = layer  # Access the only layer in the list
                # if len(layer) == 1:
                css_content.append(f"""
                    .imageBox {{
                        width: {width}px;
                        height: {height}px;
                        position: absolute;
                        left: {x1}px;
                        top: {y1}px;
                        z-index: 1;
                    }}
                    .imageBox img {{
                        width: {width}px;
                        height: {height}px;
                        object-fit: cover;
                    }}
                """)
                print(f"Processed image: {sanitized_name}")

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
    if layer.name == "backgroundColor":
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
                '<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap" rel="stylesheet" />',
                '<link rel="stylesheet" href="https://digital.mediaferry.com/animation.css">',
                '<link rel="stylesheet" href="./css/style.css" />',
                '</head>',
                '<body>',
                '<div class="container" id="sd_bgcolor_Main-Background">',
                '<a href="javascript:window.open(window.trackingUrl + window.clickTag)"></a>',
                '<a class="clicktru" target="_blank" href="#"></a>',
                # '<div class="contentSection">'
        ]
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
    '''
    .contentSection {
        width: 225px; 
        height: 166px;
        overflow: hidden;
        position: absolute; 
        left: 0px; 
        top: 73px;
        border-radius: 0 79px 79px 0;
}'''

    ]

for layer in psd:
    process_layer(layer, html_content, css_content)

with open(f'output/{file_name_t}/index.html', 'w') as f:
    f.write("\n".join(html_content))

with open(f'output/{file_name_t}/css/style.css', 'w') as f:
    f.write("\n".join(css_content))

print("HTML and CSS files generated.")

html_content.append('''

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