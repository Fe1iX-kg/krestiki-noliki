// Извлечение roomId из URL (например, "/game/16/" → roomId = 16)
const roomId = window.location.pathname.split('/')[2];
console.log('Room ID:', roomId);

// Получение состояния игры
async function fetchGameState() {
    console.log('Fetch game state status:');
    const response = await fetch(`/api/rooms/${roomId}/game/`, {
        credentials: 'include'
    });
    console.log('Fetch game state status:', response.status);
    const data = await response.json();
    console.log('Game state:', data);
    return data;
}

// Обновление UI
async function updateUI() {
    const state = await fetchGameState();
    const board = state.board;
    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        cell.textContent = board[index] === ' ' ? '' : board[index];
    });

    const status = document.getElementById('status');
    if (state.winner) {
        status.textContent = `Winner: ${state.winner.username}`;
    } else if (state.is_finished) {
        status.textContent = "Draw!";
    } else {
        status.textContent = `Current player: ${state.current_player.username}`;
    }
}

// Обработка клика по клетке
// Обработка клика по клетке
function handleCellClick(index) {
    return async (e) => {
        try {
            const response = await fetch(`/api/rooms/${roomId}/game/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify({ index: index }) // Изменили 'position' на 'index'
            });
            console.log('Move response status:', response.status);
            if (!response.ok) {
                const text = await response.text();
                console.log('Move response text:', text);
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            await updateUI();
        } catch (error) {
            console.error('Error making move:', error);
            alert('Failed to make move: ' + error.message);
        }
    };
}

// Получение CSRF-токена
function getCookie(name) {
    console.log('Getting cookie:', name);
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    console.log('CSRF token:', cookieValue);
    return cookieValue;
}

// Инициализация игры
document.addEventListener('DOMContentLoaded', async () => {
    await updateUI();

    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        cell.addEventListener('click', handleCellClick(index));
    });

    const newGameButton = document.getElementById('new-game');
    newGameButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/api/rooms/${roomId}/new_game/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify({})
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            await updateUI();
        } catch (error) {
            console.error('Error starting new game:', error);
            alert('Failed to start new game: ' + error.message);
        }
    });
});