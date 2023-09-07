from PIL import Image, ImageOps
import sys
import json
import requests

# GLOBAL VARS
# greyscale represented as ASCII characters
# credit to Paul Bourke http://paulbourke.net/dataformats/asciiart/
scale = list('$@B%8&WM#oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?*+~<>i!lI;:,-"^_`\'. ')

def convert_to_ascii(image_path, inputwidth):
    print("Generating ascii art of image at ", image_path)
    # open image with pillows
    # surface level error checking. could be much better
    try:
        img = Image.open(image_path)
    except:
        sys.exit("Error converting image")    

    # checking for transparent pixels in img
    transparency = has_transparency(img)

    if transparency:
        # print("Image contains transparent pixels")
        # if image contains transparency, filters will not work
        success_edit = False
    else:
        # print("Image does not contain transparent pixels")
        # attempting to apply posterize and contrast filters on throwaway variables
        try:
            img1 = ImageOps.posterize(img, 3)
            img1 = ImageOps.autocontrast(img)
            success_edit = True
        # if application of filters throws error, don't attempt on actual img variable
        except:
            print("Error adjusting contrast and posterizing")
            success_edit = False

    # if application of filters is successful, apply them to actual img variable
    if success_edit:
        img = apply_filters(img)

    # resizing image to smaller size
    # width fixed at 120 px, height determined by aspect ratio
    width, height = img.size
    aspect_ratio = height/width
    # NOTE: make this adjustable
    new_width = inputwidth
    new_height = aspect_ratio * new_width * 0.55
    img = img.resize((new_width, int(new_height)))

    # convert image to greyscale
    img = img.convert("L")
    
    pixels = img.getdata()
    pixels = list(pixels)
    # if image contains transparent pixels, normalize them all to white
    # this is done b/c the value of transparent pixels is 0, which shows up black
    # causes issues when image is a black 'silhouette' on transparent background
    if transparency:
        for i in range (0, len(pixels)):
            if not pixels[i]:
                pixels[i] = 256 
    new_pixels = [scale[int(pixel/3.71014492)] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
    ascii_image = "\n".join(ascii_image)

    # writes ASCII art to a file called art.txt, in same directory as src
    with open("art.txt", "w") as filew:
        filew.write(ascii_image)

# returns true if image contains transparent pixels
# credit to Jose Manuel Sanchez on StackOverflow
def has_transparency(img):
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    return False

# applies posterization and contrast filters on an image
# img must be opened with pillow module
def apply_filters(img):
    img = ImageOps.posterize(img, 3)
    img = ImageOps.autocontrast(img)
    return img

# asks the user for a search query, then returns a variable containing
# the search results. also stores the json file locally for examination
def user_query(query):
    # user input for what image they want to search for
    # %20 represents a space in URL
    search_query = query
    search_query.replace(' ', '%20')

    # calling Google custom search engine API for image search
    # pulls first 5 images from results, all PNG images
    # includes error handling for multiple error types
    try:
        r = requests.get('https://www.googleapis.com/customsearch/v1?num=10&searchType=image&fileType=jpg&key=AIzaSyB3fwhhgJPONPjDu7PflyW2Fw8aytnyKT4&cx=1559cdb99a0b943d2&q=' + search_query)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        sys.exit("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        sys.exit("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        sys.exit("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        sys.exit("Uknown error has occurred:",err)

    # writing API response into a local JSON file (same directory as src) 'imageresults.json'
    jsonResponse = r.json()
    with open('imageresults.json', 'w') as pf:
        json.dump(jsonResponse, pf, indent=4)

    # returns json variable containing search results
    return jsonResponse

# takes results of image search as a json file, pulls 5 valid image links out of this file,
# and stores and returns these links as a list
# if <5 valid links in json file, throws an error and exits
def json_urls(jsonfile):
    x, image_urls, names = 0, [], []
    for i in range(10):
        index = jsonfile['items'][i]['link'].find(".jpg")
        if index == -1: pass
        else:
            url = jsonfile['items'][i]['link'][:index+4]
            name = url.split('/')[-1]
            if name in names: pass
            else:
                names.append(name)
                print("URL " + str(i) + " = " + url)
                image_urls.append(url)
    return image_urls