"""python-for-android requires this exact entry point filename."""

def main():
    from main_android import XSMBApp
    XSMBApp().run()


if __name__ == '__main__':
    main()
