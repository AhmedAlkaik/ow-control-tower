import re

with open("index.html", "r", encoding="utf-8") as f:
    idx = f.read()

with open("ui.html", "r", encoding="utf-16") as f:
    ui = f.read()

with open("js.html", "r", encoding="utf-16") as f:
    js = f.read()

ui = ui.replace('<div class="loader" id="loader"></div>', '')
ui = ui.replace('<div id="error-msg"></div>', '')
ui_block = f'''
    <!-- FORM VIEW (SPA mode) -->
    <div id="view-form" style="display: none; animation: fadeIn 0.3s ease; padding: 20px;">
        <button class="btn secondary" onclick="showDashboard()" style="margin-bottom: 25px;"><i class="fas fa-arrow-left"></i> Back to Dashboard</button>
        {ui}
    </div>
'''

idx = idx.replace('        <script>', ui_block + '\n        <script>')

match = re.search(r'(function processRowSelection.*?<\/script>)', js, flags=re.DOTALL)
if match:
    js_functions = match.group(1).replace('</script>', '').strip()
else:
    js_functions = js

js_functions = js_functions.replace('new Array(36).fill("")', 'new Array(48).fill("")')

js_48_replacements = r'''            currentPoNo = String(data[5] || "");
            currentPrNo = String(data[2] || "");
            
            let stateStr = data[1] || "Initiated Order";
            if (!data[2] && !data[3] && !data[15]) stateStr = "Initiated Order";

            let ctx = {
                row: rowIdx,
                state: stateStr,
                prNo: currentPrNo,
                userEmail: localStorage.getItem('ow_current_user'),
                poNo: currentPoNo,
                supplier: formatIfDate(data[12]),
                blNo: formatIfDate(data[29]),
                piNo: formatIfDate(data[13]),
                delTerm: formatIfDate(data[26]),
                colorConfig: getStateColorConfig(stateStr),
                rawObj: {
                    state: formatIfDate(data[1]),
                    prNo: formatIfDate(data[2]),
                    prDate: formatIfDate(data[3]),
                    poNo: formatIfDate(data[5]),
                    poIssDate: formatIfDate(data[7]),
                    poApprDate: formatIfDate(data[8]),
                    reqDelDate: formatIfDate(data[9]),
                    company: formatIfDate(data[10]),
                    supplier: formatIfDate(data[12]),
                    piNo: formatIfDate(data[13]),
                    desc: formatIfDate(data[15]),
                    qty: formatIfDate(data[16]),
                    fob: formatIfDate(data[19]),
                    cif: formatIfDate(data[20]),
                    value: formatIfDate(data[21]),
                    currency: formatIfDate(data[22]),
                    payTerm: formatIfDate(data[24]),
                    acid: formatIfDate(data[25]),
                    delTerm: formatIfDate(data[26]),
                    commInv: formatIfDate(data[28]),
                    blNo: formatIfDate(data[29]),
                    etd: formatIfDate(data[30]),
                    eta: formatIfDate(data[31]),
                    shipRelease: formatIfDate(data[34]),
                    containers: formatIfDate(data[35]),
                    containerType: formatIfDate(data[36]),
                    bank: formatIfDate(data[37]),
                    bankDate: formatIfDate(data[38]),
                    estReadiness: formatIfDate(data[39]),
                    leadTime: formatIfDate(data[41]),
                    vendorEmail: formatIfDate(data[43]),
                    buyerEmail: formatIfDate(data[44]) || localStorage.getItem('ow_current_user') || "",
                    comments: formatIfDate(data[47])
                }
            };'''
js_functions = re.sub(r'currentPoNo = String\(data\[8\].*?leadTime: formatIfDate\(data\[35\]\)\n\s*\}\n\s*\};', js_48_replacements, js_functions, flags=re.DOTALL)

js_functions = js_functions.replace("'v-docArrival': 'docArrival', ", "")
js_functions = js_functions.replace("'v-docArrival': '2026-09-08',", "")
js_functions = js_functions.replace("'v-docArrival', ", "")
js_functions = js_functions.replace(", 'v-docArrival'", "")

js_functions = js_functions.replace("Office.context.ui.messageParent(JSON.stringify(payload));", "processMessage({ message: JSON.stringify(payload) });")
js_functions = js_functions.replace("document.getElementById('loader').style.display = 'block';", "")
js_functions = js_functions.replace("document.getElementById('loader').style.display = 'none';", "")

js_globals = r'''
            // SPA FORM VARIABLES
            let currentRow = -1;
            let currentState = "Initiated Order";
            let currentPoNo = "";
            let currentPrNo = "";
            let currentRowData = new Array(48).fill(""); // Stores the active live data
            let lastCtxRaw = null; // Cache last row data for form toggling
'''
idx = idx.replace('        <script>', '        <script>\n' + js_globals)
idx = idx.replace('</script>', '\n' + js_functions + '\n        </script>', 1)

show_functions = r'''            function showActionForm() {
                const viewDash = document.getElementById('view-dash');
                const viewForm = document.getElementById('view-form');

                if (!viewForm) {
                    onError("Error: The #view-form container is missing from the HTML. Please wrap the form UI properly.");
                    return;
                }

                viewDash.style.display = 'none';
                viewForm.style.display = 'block';

                // Use the globally stored row data, or default to empty if a new row
                if (lastRowIdx > 0 && currentRowData.length > 0) {
                    processRowSelection(lastRowIdx + 1, currentRowData);
                } else {
                    processRowSelection(-1, new Array(48).fill(""));
                }
            }

            function showDashboard() {
                document.getElementById('view-form').style.display = 'none';
                document.getElementById('view-dash').style.display = 'block';
            }'''
idx = re.sub(r'function showActionForm\(\) \{.*?\}', show_functions, idx, flags=re.DOTALL)

poll_search = r'''                        let data = range.values[0];
                        let state = data[1] || "Initiated Order";
                        // If row is totally blank
                        if (!data[1] && !data[2] && !data[3]) state = "Initiated Order";'''
poll_replace = r'''                        let data = range.values[0];
                        let state = data[1] || "Initiated Order";
                        // If row is totally blank
                        if (!data[1] && !data[2] && !data[3]) state = "Initiated Order";

                        currentRowData = data;

                        // Live Adaptation: If the form is currently visible, update it instantly when selection changes
                        const viewForm = document.getElementById('view-form');
                        if (viewForm && viewForm.style.display === 'block') {
                            processRowSelection(r + 1, data);
                        }'''
idx = idx.replace(poll_search, poll_replace)

idx = re.sub(r'window\.addEventListener\(\'message\',.*?\}\);', '', idx, flags=re.DOTALL)
idx = idx.replace('if (dialog) dialog.close();', '')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(idx)
