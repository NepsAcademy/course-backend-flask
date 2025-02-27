import os
from factory import create_app

ConfigClass = os.environ.get("CONFIG_CLASS", "config.DevelopmentConfig")

app = create_app(ConfigClass)

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
