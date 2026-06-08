document.addEventListener('DOMContentLoaded', () => {
    setupRouteAwareFlightSearch();
    setupAirportSelectionControls();
    setupBootstrapToasts();
    setupPaymentMethodSelection();
    setupFlexibleDateCarousel();
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

function setupPaymentMethodSelection() {
    const paymentGrid = document.querySelector('.payment-method-grid');
    if (!paymentGrid) {
        return;
    }

    paymentGrid.addEventListener('change', (event) => {
        const radio = event.target;
        if (radio && radio.name === 'metodo') {
            paymentGrid.querySelectorAll('.payment-method-option').forEach((option) => {
                option.classList.remove('is-selected');
            });
            const label = radio.closest('.payment-method-option');
            if (label) {
                label.classList.add('is-selected');
            }
        }
    });
}

function setupFlexibleDateCarousel() {
    document.querySelectorAll('[data-flex-date-carousel]').forEach((carousel) => {
        carousel.addEventListener('click', (event) => {
            const button = event.target.closest('[data-flex-date-arrow]');
            if (!button || button.disabled) {
                return;
            }

            event.preventDefault();
            loadFlexibleDates(carousel, button);
        });
    });
}

async function loadFlexibleDates(carousel, button) {
    const strip = carousel.querySelector('[data-flex-date-strip]');
    const url = button.dataset.url;
    if (!strip || !url) {
        return;
    }

    const direction = button.dataset.flexDateArrow === 'next' ? 'next' : 'previous';
    const movementClass = direction === 'next' ? 'is-moving-left' : 'is-moving-right';
    const enterClass = direction === 'next' ? 'is-entering-right' : 'is-entering-left';
    const buttons = carousel.querySelectorAll('[data-flex-date-arrow]');

    buttons.forEach((arrow) => {
        arrow.disabled = true;
    });
    carousel.setAttribute('aria-busy', 'true');
    strip.classList.remove('is-entering-left', 'is-entering-right');
    strip.classList.add(movementClass);

    try {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        if (!response.ok) {
            throw new Error('Nao foi possivel carregar as datas.');
        }

        const payload = await response.json();
        await waitForAnimationFrame();
        renderFlexibleDates(strip, payload.dates || []);
        updateDateArrow(carousel, 'previous', payload.previousUrl);
        updateDateArrow(carousel, 'next', payload.nextUrl);

        strip.classList.remove(movementClass);
        strip.classList.add(enterClass);

        if (payload.windowUrl && window.history?.replaceState) {
            window.history.replaceState({}, '', payload.windowUrl);
        }
    } catch (error) {
        strip.classList.remove(movementClass);
        console.error(error);
    } finally {
        carousel.removeAttribute('aria-busy');
        buttons.forEach((arrow) => {
            arrow.disabled = !arrow.dataset.url;
        });
        window.setTimeout(() => {
            strip.classList.remove('is-entering-left', 'is-entering-right');
        }, 320);
    }
}

function renderFlexibleDates(strip, dates) {
    strip.replaceChildren(...dates.map(createDateChip));
}

function createDateChip(dateInfo) {
    const chip = document.createElement('a');
    chip.className = 'flex-date-chip';
    chip.href = dateInfo.url || '#';
    chip.setAttribute('aria-label', dateInfo.ariaLabel || 'Buscar voos nesta data');

    if (dateInfo.selected) {
        chip.classList.add('is-selected');
    }
    if (!dateInfo.hasFlight) {
        chip.classList.add('is-empty');
    }

    const label = document.createElement('span');
    label.textContent = dateInfo.label || '';
    chip.appendChild(label);

    if (dateInfo.price) {
        const price = document.createElement('strong');
        price.textContent = dateInfo.price;
        chip.appendChild(price);
    } else {
        const empty = document.createElement('small');
        empty.textContent = 'Sem voo';
        chip.appendChild(empty);
    }

    return chip;
}

function updateDateArrow(carousel, direction, url) {
    const arrow = carousel.querySelector(`[data-flex-date-arrow="${direction}"]`);
    if (!arrow) {
        return;
    }

    arrow.dataset.url = url || '';
    arrow.disabled = !url;
}

function waitForAnimationFrame() {
    return new Promise((resolve) => {
        window.setTimeout(resolve, 180);
    });
}
