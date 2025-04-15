console.log('lobby.js loaded');
        document.getElementById('join-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Join form submitted');
            const code = document.getElementById('room-code').value.trim();
            if (!code) {
                alert('Please enter a room code');
                return;
            }
            try {
                const response = await fetch('/api/rooms/join/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    credentials: 'include', // Убедись, что это есть
                    body: JSON.stringify({ code: code })
                });
                console.log('Join response status:', response.status);
                console.log('Join response headers:', response.headers.get('content-type'));
                if (!response.ok) {
                    const text = await response.text();
                    console.log('Join response text:', text);
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const data = await response.json();
                window.location.href = `/game/${data.room.id}/`;
            } catch (error) {
                console.error('Error joining room:', error);
                alert('Failed to join room: ' + error.message);
            }
        });

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