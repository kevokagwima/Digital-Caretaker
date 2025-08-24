// Image upload functionality
document.addEventListener("DOMContentLoaded", function () {
  const uploadArea = document.getElementById("upload-area");
  const fileInput = document.getElementById("image-upload");
  const previewArea = document.getElementById("image-preview");

  // Click on upload area to trigger file input
  uploadArea.addEventListener("click", function () {
    fileInput.click();
  });

  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight drop area when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });

  // Handle dropped files
  uploadArea.addEventListener("drop", handleDrop, false);

  // Handle selected files
  fileInput.addEventListener("change", handleFiles, false);

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight() {
    uploadArea.style.borderColor = "var(--primary)";
    uploadArea.style.backgroundColor = "rgba(79, 70, 229, 0.05)";
  }

  function unhighlight() {
    uploadArea.style.borderColor = "var(--border)";
    uploadArea.style.backgroundColor = "transparent";
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files } });
  }

  function handleFiles(e) {
    const files = e.target.files;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      if (!file.type.match("image.*")) continue;

      if (previewArea.children.length >= 6) {
        alert("Maximum 6 images allowed");
        break;
      }

      const reader = new FileReader();

      reader.onload = function (e) {
        const previewItem = document.createElement("div");
        previewItem.className = "preview-item";

        const img = document.createElement("img");
        img.src = e.target.result;
        img.className = "preview-image";

        const removeBtn = document.createElement("div");
        removeBtn.className = "remove-image";
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.addEventListener("click", function () {
          previewItem.remove();
        });

        previewItem.appendChild(img);
        previewItem.appendChild(removeBtn);
        previewArea.appendChild(previewItem);
      };

      reader.readAsDataURL(file);
    }
  }
});
