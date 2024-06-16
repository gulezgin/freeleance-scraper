import requests
from bs4 import BeautifulSoup
import json

# URL of the web page
url = 'https://tr.aliexpress.com/item/1005006338551554.html?spm=a2g0o.categorymp.prodcutlist.28.a285t7s2t7s2dq&pdp_ext_f=%7B%22sku_id%22%3A%2212000036814952011%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3A'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts: 
        if 'window.runParams' in script.text: 
            # We found window.runParams data
            script_text = script.text.strip()
            # Let's extract the contents of window.runParams
            start_index = script_text.find('{')
            end_index = script_text.rfind('}') + 1
            run_params_json = script_text[start_index:end_index]

            # Let's save JSON data to file
            with open('run_params.json', 'w', encoding='utf-8') as file:
                file.write(run_params_json)
            
            print("window.runParams saved successfully.")
            break  
    else:
        print("window.runParams not found.")
else:
    print("Error: There was a problem loading the page.")

# Let's read the JSON file
with open('run_params.json', 'r', encoding='utf-8') as file:
    run_params = json.load(file)

# Let's convert JSON data into JavaScript code
run_params_js = json.dumps(run_params, ensure_ascii=False)

# Let's create the JavaScript code
javascript_code = f"""
(function() {{
    // Let's load the window.runParams data
    window.runParams = {run_params_js};

    function getVariants() {{
        if (typeof window.runParams === 'undefined' || typeof window.runParams.data === 'undefined') {{
            console.error('runParams object or data does not exist.');
            return [];
        }}
        let skuComponent = window.runParams.data.skuComponent;
        if (!skuComponent) {{
            console.error('SKU Component data not found.');
            return [];
        }}
        let skuPropertyList = skuComponent.productSKUPropertyList;
        if (!skuPropertyList) {{
            console.error('SKU Property List not found.');
            return [];
        }}
        let variants = [];
        skuPropertyList.forEach((property) => {{
            let propertyName = property.skuPropertyName;
            let propertyValues = property.skuPropertyValues;
            propertyValues.forEach((value) => {{
                let variant = {{
                    name: propertyName,
                    value: value.propertyValueName,
                    displayValue: value.propertyValueDisplayName,
                    color: value.skuColorValue || null,
                    image: value.skuPropertyImagePath || null
                }};
                variants.push(variant);
            }});
        }});
        return variants;
    }}
    setTimeout(() => {{
        try {{
            let variants = getVariants();
            console.log('Product Variants:', variants);
            console.log(JSON.stringify(variants, null, 2));
        }} catch (error) {{
            console.error('An error occurred while retrieving variant information:', error);
        }}
    }}, 3000);
}})();
"""

# Let's write the generated JavaScript code to the file
with open('script.js', 'w', encoding='utf-8') as file:
    file.write(javascript_code)

print("JavaScript code was successfully generated and saved in script.js file.")

