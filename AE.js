const fs = require('fs');

// Function to extract `data:` sections from the file content
function extractDataSections(fileContent) {
    const dataSections = [];
    const dataRegex = /data: \{([^]*?)\}(?=,\s+\w+:|\s*$)/g;  // Improved regex to match 'data: { ... }'
    let match;
    while ((match = dataRegex.exec(fileContent)) !== null) {
        dataSections.push(match[1]); // Extract the content inside 'data: { ... }'
    }
    return dataSections.join(','); // Join all sections with commas
}
// Read the content of the txt file
const txtFileName = 'dosya_temiz.txt';  // Replace with the actual file name
const fileContent = fs.readFileSync(txtFileName, 'utf-8');

// Extract `data:` sections
const extractedData = extractDataSections(fileContent);

// Construct the `runParams` object
const runParams = {
    window: {
        runParams: {
            data: JSON.parse(`{${extractedData}}`),  // Parse the extracted data string into an object
            is23: true
        },
        _d_c_: {
            viewName: 'choiceDetail',
            isCSR: false
        }
    }
};

// Convert `runParams` object to JSON string with pretty formatting
const jsonData = JSON.stringify(runParams, null, 2);

// Write JSON data to file
const outputFileName = 'Z3runParams.json';
fs.writeFileSync(outputFileName, jsonData);

console.log(`JSON verisi '${outputFileName}' dosyasına başarıyla kaydedildi.`);
