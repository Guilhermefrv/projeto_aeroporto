document.addEventListener('DOMContentLoaded', () => {
    if (!window.bootstrap) {
        return;
    }

    document.querySelectorAll('.toast').forEach((toastElement) => {
        const toast = bootstrap.Toast.getOrCreateInstance(toastElement, {
            autohide: true,
            delay: 4200,
        });

        toast.show();
    });
});
