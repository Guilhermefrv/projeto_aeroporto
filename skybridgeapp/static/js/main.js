document.addEventListener('DOMContentLoaded', () => {
    setupRouteAwareFlightSearch();

    if (window.bootstrap) {
        document.querySelectorAll('.toast').forEach((toastElement) => {
            const toast = bootstrap.Toast.getOrCreateInstance(toastElement, {
                autohide: true,
                delay: 4200,
            });

            toast.show();
        });
    }
});

function setupRouteAwareFlightSearch() {
    const routeMapElement = document.getElementById('route-map-data');
    if (!routeMapElement) {
        return;
    }

    let routeMap = {};
    try {
        routeMap = JSON.parse(routeMapElement.textContent || '{}');
    } catch (error) {
        routeMap = {};
    }

    document.querySelectorAll('.flight-search-form').forEach((form) => {
        const originSelect = form.querySelector('select[name="origem"]');
        const destinationSelect = form.querySelector('select[name="destino"]');
        const routeHelper = form.querySelector('[data-route-helper]');

        if (!originSelect || !destinationSelect) {
            return;
        }

        const updateDestinations = () => {
            const originCode = getAirportCode(originSelect.selectedOptions[0]?.textContent);
            const allowedDestinations = routeMap[originCode] || [];
            let selectedDestinationIsAvailable = true;

            Array.from(destinationSelect.options).forEach((option) => {
                if (!option.value) {
                    option.hidden = false;
                    option.disabled = false;
                    return;
                }

                const destinationCode = getAirportCode(option.textContent);
                const isAvailable = !originCode || allowedDestinations.includes(destinationCode);
                option.hidden = !isAvailable;
                option.disabled = !isAvailable;

                if (option.selected && !isAvailable) {
                    selectedDestinationIsAvailable = false;
                }
            });

            if (!selectedDestinationIsAvailable) {
                destinationSelect.value = '';
            }

            if (routeHelper) {
                if (!originCode) {
                    routeHelper.textContent = 'Escolha uma origem para ver destinos disponiveis.';
                } else if (allowedDestinations.length) {
                    routeHelper.textContent = `Destinos disponiveis saindo de ${originCode}: ${allowedDestinations.join(', ')}.`;
                } else {
                    routeHelper.textContent = 'Ainda nao ha destinos cadastrados para essa origem.';
                }
            }
        };

        originSelect.addEventListener('change', updateDestinations);
        updateDestinations();
    });
}

function getAirportCode(label = '') {
    return label.split('-')[0].trim().toUpperCase();
}
