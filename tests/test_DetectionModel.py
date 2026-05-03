# TODO: Write tests for your package using pytest
import DetectionModel as dm

Source = "tests/stop.mp4"

app = dm.Model(Source)

app.video()

