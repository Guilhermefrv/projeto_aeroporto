document.addEventListener('DOMContentLoaded', () => {
    setupRouteAwareFlightSearch();
    setupAirportSelectionControls();
    setupBootstrapToasts();
});

function setupBootstrapToasts() {
    if (window.bootstrap) {
        document.querySelectorAll('.toast').forEach((toastElement) => {
            const toast = bootstrap.Toast.getOrCreateInstance(toastElement, {
                autohide: true,
                delay: 4200,
            });

            toast.show();
        });
    }
}

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
        if (!originSelect || !destinationSelect) {
            return;
        }

        const routeHelpers = [
            ...form.querySelectorAll('[data-route-helper]'),
            ...document.querySelectorAll('.destination-modal-helper[data-route-helper]'),
        ];
        const destinationOptionButtons = document.querySelectorAll(
            `[data-destination-option][data-target-select="${destinationSelect.id}"]`
        );

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

            destinationOptionButtons.forEach((button) => {
                const destinationCode = button.dataset.airportCode;
                const isAvailable = !originCode || allowedDestinations.includes(destinationCode);
                button.hidden = !isAvailable;
                button.disabled = !isAvailable;
            });

            if (!selectedDestinationIsAvailable) {
                destinationSelect.value = '';
            }

            updateSearchDisplay(originSelect);
            updateSearchDisplay(destinationSelect);
            updateAirportOptionSelection(originSelect);
            updateAirportOptionSelection(destinationSelect);

            routeHelpers.forEach((routeHelper) => {
                if (!originCode) {
                    routeHelper.textContent = 'Escolha uma origem para ver destinos disponiveis.';
                } else if (allowedDestinations.length) {
                    routeHelper.textContent = `Destinos disponiveis saindo de ${originCode}: ${allowedDestinations.join(', ')}.`;
                } else {
                    routeHelper.textContent = 'Ainda nao ha destinos cadastrados para essa origem.';
                }
            });
        };

        originSelect.addEventListener('change', updateDestinations);
        destinationSelect.addEventListener('change', () => {
            updateSearchDisplay(destinationSelect);
            updateAirportOptionSelection(destinationSelect);
        });
        updateDestinations();
    });
}

function getAirportCode(label = '') {
    return label.split('-')[0].trim().toUpperCase();
}

function setupAirportSelectionControls() {
    document.addEventListener('click', (event) => {
        const airportButton = event.target.closest('[data-airport-option]');
        if (airportButton) {
            handleAirportOptionClick(airportButton);
            return;
        }

        const swapButton = event.target.closest('.route-swap-button');
        if (swapButton) {
            handleRouteSwapClick(swapButton);
        }
    });

    document.querySelectorAll('[data-airport-option]').forEach((button) => {
        button.setAttribute('aria-pressed', 'false');
    });

    document.querySelectorAll('select[name="origem"], select[name="destino"]').forEach((select) => {
        updateSearchDisplay(select);
        updateAirportOptionSelection(select);
    });
}

function handleAirportOptionClick(button) {
    if (button.disabled) {
        return;
    }

    const select = document.getElementById(button.dataset.targetSelect);
    if (!select) {
        return;
    }

    select.value = button.dataset.airportValue;
    select.dispatchEvent(new Event('change', { bubbles: true }));
    updateSearchDisplay(select);
    updateAirportOptionSelection(select);
}

function handleRouteSwapClick(button) {
    const form = button.closest('form');
    const originSelect = form?.querySelector('select[name="origem"]');
    const destinationSelect = form?.querySelector('select[name="destino"]');
    if (!originSelect || !destinationSelect) {
        return;
    }

    const originValue = originSelect.value;
    originSelect.value = destinationSelect.value;
    destinationSelect.value = originValue;
    originSelect.dispatchEvent(new Event('change', { bubbles: true }));
    destinationSelect.dispatchEvent(new Event('change', { bubbles: true }));
    updateSearchDisplay(originSelect);
    updateSearchDisplay(destinationSelect);
    updateAirportOptionSelection(originSelect);
    updateAirportOptionSelection(destinationSelect);
}

function updateSearchDisplay(select) {
    const form = select.closest('form');
    const display = form?.querySelector(`[data-search-display-label="${select.name}"]`)
        || document.querySelector(`[data-search-display-label="${select.name}"]`);
    if (!display) {
        return;
    }

    const selectedOption = select.selectedOptions[0];
    const fallback = select.name === 'origem' ? 'Insira uma origem' : 'Insira um destino';
    display.textContent = selectedOption && selectedOption.value ? selectedOption.textContent.trim() : fallback;

    const pickerField = display.closest('[data-search-display]');
    if (pickerField) {
        pickerField.classList.toggle('is-filled', Boolean(selectedOption && selectedOption.value));
    }
}

function updateAirportOptionSelection(select) {
    document
        .querySelectorAll(`[data-airport-option][data-target-select="${select.id}"]`)
        .forEach((button) => {
            const isSelected = button.dataset.airportValue === select.value;
            button.classList.toggle('is-selected', isSelected);
            button.setAttribute('aria-pressed', String(isSelected));
        });
}
