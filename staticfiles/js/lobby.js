console.log('lobby.js loaded - Start');

// Тестовая отладка
console.log('Testing JavaScript execution');

// Проверяем, загружен ли DOM
console.log('DOM readyState:', document.readyState);

// Проверяем, существует ли ссылка
const createRoomLink = document.getElementById('create-room-link');
if (!createRoomLink) {
    console.error('Link with id "create-room-link" not found');
    console.log('All links:', document.querySelectorAll('a'));
    console.log('Document body:', document.body.innerHTML);
} else {
    console.log('Link found:', createRoomLink);
    createRoomLink.addEventListener('click', async (e) => {
        e.preventDefault();
        console.log('Create room link clicked');
        try {
            const response = await fetch('/api/rooms/', {
                method: `POST`,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify({})
            });
            console.log('Create room response status:', response.status);
            if (!response.ok) {
                const text = await response.text();
                console.log('Create room response text:', text);
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Create room data:', data);
            window.location.href = `/game/${data.id}/`;
        } catch (error) {
            console.error('Error creating room:', error);
            alert('Failed to create room: ' + error.message);
        }
    });
}

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

console.log('lobby.js loaded - End');