import {parseSingletons} from 'singleton-argv'; console.log(JSON.stringify(parseSingletons({
  "args": [
    "--target",
    "east"
  ],
  "options": {
    "target": {
      "type": "string"
    }
  }
}),null,2));