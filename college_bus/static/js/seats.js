// Seat Selection Logic

document.addEventListener('DOMContentLoaded', function () {
    const seatElements = document.querySelectorAll('.bus-seat.available');
    const occupiedSeats = document.querySelectorAll('.bus-seat.occupied');
    const selectedSeatInput = document.getElementById('selectedSeatInput');
    const selectedSeatDisplay = document.getElementById('selectedSeatDisplay');
    const proceedBtn = document.getElementById('proceedToPaymentBtn');

    seatElements.forEach(seat => {
        seat.addEventListener('click', function () {
            const seatNumber = this.getAttribute('data-seat-number');

            // If this seat was already selected, deselect it
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                this.classList.add('available');
                selectedSeatInput.value = '';
                selectedSeatDisplay.innerText = 'None';
                if (proceedBtn) proceedBtn.disabled = true;
                return;
            }

            // Remove selected class from any other seat
            document.querySelectorAll('.bus-seat.selected').forEach(s => {
                s.classList.remove('selected');
                s.classList.add('available');
            });

            // Select this seat
            this.classList.remove('available');
            this.classList.add('selected');

            selectedSeatInput.value = seatNumber;
            selectedSeatDisplay.innerText = `Seat ${seatNumber}`;
            if (proceedBtn) proceedBtn.disabled = false;
        });
    });

    occupiedSeats.forEach(seat => {
        seat.addEventListener('click', function () {
            const seatNumber = this.getAttribute('data-seat-number');
            alert(`Seat ${seatNumber} is already occupied and locked for this academic year.`);
        });
    });
});
