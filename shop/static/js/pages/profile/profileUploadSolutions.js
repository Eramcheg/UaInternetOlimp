
document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.upload-box input[type="file"]').forEach(input => {
        input.addEventListener('change', async (e) => {
          const file = e.target.files && e.target.files[0];
          if (!file) return;

          const uploadBox = e.target.closest('.upload-box');
          const boxId = uploadBox ? uploadBox.id : '';
          const nameSpan = uploadBox?.querySelector('.file-name');
          if (nameSpan) nameSpan.textContent = file.name;

          const formData = new FormData();
          formData.append('file', file);
          formData.append('box_id', boxId);

          try {
            const resp = await fetch(profileConfig.uploadSolutionUrl, {
              method: 'POST',
              headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
              },
              body: formData,
              credentials: 'same-origin',
            });

            const contentType = resp.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
              throw new Error(`Unexpected response type: ${contentType}`);
            }

            const data = await resp.json();
            if (data.success) {
              window.location.reload();
            } else {
              console.error('Upload failed:', data.error || data);
            }
          } catch (err) {
            console.error('Upload error:', err);
          }
        });
    });
});