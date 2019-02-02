from src.dragon import wakeup, fly_away

if __name__ == "__main__":
    try:
        dragone = wakeup()
        fly_away(dragone)
    except:
        raise
