from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("\n🎵 SoundWave Music Platform Starting...")
    print("🌐 Open http://127.0.0.1:5000 in your browser")
    print("👤 Default admin: admin@soundwave.com / admin123\n")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
