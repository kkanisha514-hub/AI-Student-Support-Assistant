// =====================================================
// CampusAI Admin - Knowledge Base
// =====================================================


// API base URL
const API_BASE = "/api";


// =====================================================
// DOM ELEMENTS
// =====================================================

const uploadForm =
    document.getElementById("uploadForm");

const fileInput =
    document.getElementById("fileInput");

const selectedFileName =
    document.getElementById("selectedFileName");

const uploadStatus =
    document.getElementById("uploadStatus");

const uploadButton =
    document.getElementById("uploadButton");

const docList =
    document.getElementById("docList");

const documentCount =
    document.getElementById("documentCount");


// =====================================================
// FILE SELECTION
// =====================================================

fileInput.addEventListener(
    "change",
    () => {

        const file =
            fileInput.files[0];


        if (file) {

            selectedFileName.textContent =
                file.name;

        } else {

            selectedFileName.textContent =
                "Click to select a PDF or TXT file";
        }

    }
);


// =====================================================
// FORMAT FILE SIZE
// =====================================================

function formatBytes(bytes) {

    if (!bytes) {
        return "";
    }


    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (bytes < 1024 * 1024) {

        return `${(
            bytes / 1024
        ).toFixed(1)} KB`;

    }


    return `${(
        bytes /
        (1024 * 1024)
    ).toFixed(1)} MB`;
}


// =====================================================
// LOAD DOCUMENTS
// =====================================================

async function loadDocuments() {

    docList.innerHTML = `
        <li class="loading-row">
            Loading documents...
        </li>
    `;


    try {

        const response =
            await fetch(
                `${API_BASE}/documents`
            );


        console.log(
            "GET /api/documents:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                `Unable to load documents (${response.status})`
            );

        }


        const data =
            await response.json();


        console.log(
            "Documents:",
            data
        );


        // Support several possible API formats
        let documents = [];


        if (Array.isArray(data)) {

            documents = data;

        } else if (
            Array.isArray(data.documents)
        ) {

            documents = data.documents;

        } else if (
            Array.isArray(data.files)
        ) {

            documents = data.files;

        } else if (
            Array.isArray(data.items)
        ) {

            documents = data.items;

        }


        // Update count
        documentCount.textContent =
            documents.length;


        // No documents
        if (documents.length === 0) {

            docList.innerHTML = `
                <li class="empty-row">
                    No documents uploaded yet.
                </li>
            `;

            return;
        }


        // Clear list
        docList.innerHTML = "";


        // Create rows
        documents.forEach(
            (document) => {

                const filename =
                    typeof document === "string"
                        ? document
                        : (
                            document.filename ||
                            document.name ||
                            "Document"
                        );


                const size =
                    typeof document === "object"
                        ? (
                            document.size ||
                            0
                        )
                        : 0;


                const item =
                    createDocumentRow(
                        filename,
                        size
                    );


                docList.appendChild(
                    item
                );

            }
        );


    } catch (error) {

        console.error(
            "Document loading error:",
            error
        );


        docList.innerHTML = `
            <li class="empty-row">
                Unable to load documents.
            </li>
        `;


        documentCount.textContent =
            "—";
    }
}


// =====================================================
// CREATE DOCUMENT ROW
// =====================================================

function createDocumentRow(
    filename,
    size
) {

    const item =
        document.createElement("li");


    // -------------------------------------------------
    // Document info
    // -------------------------------------------------

    const info =
        document.createElement("div");

    info.className =
        "document-info";


    // -------------------------------------------------
    // File icon
    // -------------------------------------------------

    const icon =
        document.createElement("div");

    icon.className =
        "file-icon";


    icon.textContent =
        filename
            .toLowerCase()
            .endsWith(".pdf")
            ? "📕"
            : "📄";


    // -------------------------------------------------
    // Text
    // -------------------------------------------------

    const text =
        document.createElement("div");


    const name =
        document.createElement("span");

    name.className =
        "doc-name";

    name.textContent =
        filename;


    const fileSize =
        document.createElement("span");

    fileSize.className =
        "doc-size";


    fileSize.textContent =
        size
            ? formatBytes(size)
            : "Knowledge document";


    text.appendChild(
        name
    );

    text.appendChild(
        fileSize
    );


    info.appendChild(
        icon
    );

    info.appendChild(
        text
    );


    // -------------------------------------------------
    // Delete button
    // -------------------------------------------------

    const deleteButton =
        document.createElement("button");

    deleteButton.className =
        "delete-btn";

    deleteButton.textContent =
        "Delete";


    deleteButton.addEventListener(
        "click",
        () => {

            deleteDocument(
                filename
            );

        }
    );


    // -------------------------------------------------
    // Final row
    // -------------------------------------------------

    item.appendChild(
        info
    );

    item.appendChild(
        deleteButton
    );


    return item;
}


// =====================================================
// UPLOAD DOCUMENT
// =====================================================

uploadForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const file =
            fileInput.files[0];


        // -------------------------------------------------
        // No file
        // -------------------------------------------------

        if (!file) {

            showStatus(
                "Please select a document.",
                "error"
            );

            return;
        }


        // -------------------------------------------------
        // Check extension
        // -------------------------------------------------

        const extension =
            file.name
                .split(".")
                .pop()
                .toLowerCase();


        if (
            !["pdf", "txt"]
                .includes(extension)
        ) {

            showStatus(
                "Only PDF and TXT files are supported.",
                "error"
            );

            return;
        }


        // -------------------------------------------------
        // FormData
        // -------------------------------------------------

        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        // -------------------------------------------------
        // Disable button
        // -------------------------------------------------

        uploadButton.disabled =
            true;

        uploadButton.textContent =
            "Uploading...";


        showStatus(
            "Uploading and processing document...",
            ""
        );


        try {

            // -------------------------------------------------
            // Upload
            // -------------------------------------------------

            const response =
                await fetch(
                    `${API_BASE}/documents/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            console.log(
                "POST /api/documents/upload:",
                response.status
            );


            // -------------------------------------------------
            // Error
            // -------------------------------------------------

            if (!response.ok) {

                let message =
                    `Upload failed (${response.status})`;


                try {

                    const error =
                        await response.json();


                    if (error.detail) {

                        message =
                            error.detail;

                    }

                } catch (_) {

                    // Ignore JSON parsing error

                }


                throw new Error(
                    message
                );
            }


            // -------------------------------------------------
            // Success
            // -------------------------------------------------

            const result =
                await response.json();


            console.log(
                "Upload result:",
                result
            );


            showStatus(
                `✓ Document added successfully. ${result.chunks_indexed || 0} chunks indexed.`,
                "success"
            );


            // -------------------------------------------------
            // Reset file
            // -------------------------------------------------

            fileInput.value = "";


            selectedFileName.textContent =
                "Click to select a PDF or TXT file";


            // -------------------------------------------------
            // Reload document list
            // -------------------------------------------------

            await loadDocuments();


        } catch (error) {

            console.error(
                "Upload error:",
                error
            );


            showStatus(
                error.message ||
                "Unable to upload document.",
                "error"
            );


        } finally {

            uploadButton.disabled =
                false;

            uploadButton.textContent =
                "Upload & Add to Knowledge Base";

        }

    }
);


// =====================================================
// DELETE DOCUMENT
// =====================================================

async function deleteDocument(
    filename
) {

    const confirmed =
        confirm(
            `Delete "${filename}" from the knowledge base?`
        );


    if (!confirmed) {
        return;
    }


    try {

        showStatus(
            "Deleting document...",
            ""
        );


        const response =
            await fetch(
                `${API_BASE}/documents/${encodeURIComponent(filename)}`,
                {
                    method: "DELETE"
                }
            );


        console.log(
            "DELETE document:",
            response.status
        );


        if (!response.ok) {

            let message =
                "Unable to delete document";


            try {

                const error =
                    await response.json();


                if (error.detail) {

                    message =
                        error.detail;

                }

            } catch (_) {

                // Ignore JSON parsing error
            }


            throw new Error(
                message
            );
        }


        showStatus(
            "✓ Document deleted.",
            "success"
        );


        await loadDocuments();


    } catch (error) {

        console.error(
            "Delete error:",
            error
        );


        showStatus(
            error.message ||
            "Unable to delete document.",
            "error"
        );
    }
}


// =====================================================
// STATUS MESSAGE
// =====================================================

function showStatus(
    message,
    type
) {

    uploadStatus.textContent =
        message;


    uploadStatus.className =
        "status";


    if (type) {

        uploadStatus.classList.add(
            type
        );

    }
}


// =====================================================
// START
// =====================================================

loadDocuments();