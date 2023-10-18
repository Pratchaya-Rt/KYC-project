const videoElement = document.getElementsByClassName("input_video")[0];
var face_payload = null;
// set variable n_cl `var` outsite and update value with predict() ,
// for own can access this variable in other func
async function predict(x) {
  const model = await tf.loadLayersModel("/static/model.json");
  const y = await model.predict(tf.tensor(x).reshape([1, 1434])).reshape([4]);
  
  //  Value for each layer here!
  n_class = Array.from(y.argMax().dataSync())[0];
  prob = Array.from(y.max().dataSync())[0];
}

function onResults(results) {
  if (results.multiFaceLandmarks) {
    for (const landmarks of results.multiFaceLandmarks) {
      let x = [];
      for (const crd of landmarks) {
        x.push(crd.x, crd.y, crd.z);
      }
      // call predict
      predict(x);
    }
  }
}

// Initiate FaceMesh
const faceMesh = new FaceMesh({
  locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
  },
});
faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5,
});
// func for recive result detection faecmesh
faceMesh.onResults(onResults);

// Send image from video to feceMesh
const camera = new Camera(videoElement, {
  onFrame: async () => {
    await faceMesh.send({ image: videoElement });
  },
  width: 720,
  height: 720,
});

const delay = async (ms = 1000) =>
  new Promise((resolve) => setTimeout(resolve, ms));

async function check_change_page_c() {
  while (true) {
    const display = document.getElementById("page-c").style.display;
    if (display == "none") {
      break;
    }
    await delay(1000);
  }
  // start quize_process if stay in page d
  quize_process();
}

async function check_change_page_b() {
  while (true) {
    const display = document.getElementById("page-b").style.display;
    if (display == "none") {
      break;
    }
    await delay(1000);
  }
  // ! SET start CAMERA  IN PAGE c
  // camera start => facaMesh => predict => update value n_class, prob
  camera.start();
  countdown_button_able()
  
}
async function countdown_button_able()  {
const countdown_button = document.getElementById('countDonw_button')
cout_button = 5
while(true) {
  await delay(1000);
  countdown_button.innerHTML= String(cout_button)
  if (cout_button < 1) {
    break
  }
  cout_button-= 1
}
countdown_button.innerText= 'Allow'
countdown_button.disabled= false
}







// *1. camera start between page c (Notify the requirements page)
check_change_page_b();

// *2. if change page c => d, start quize_process fucn
// page c to d => Process check each comand OM, TL, TR, Update avatar, Text command
check_change_page_c();

// Initiate 4: false
const sign_text = [
  "Please open your mouth.",
  "Please place your face in the center of the circle.",
  "Please turn your face to the left.",
  "Please turn your face to the right.",
];
const face_class = ["OM", "S", "TL", "TR", false];
const face_check_ = [0, 2, 3, 1];
// const face_check_ = [1];
var n_class = 4;
var prob = 0;

async function quize_process() {
  let face_stand = 0;
  while (true) {
    // Send message
    document.getElementById("text-sign").innerHTML = sign_text[1];
    document.getElementById(
      "avatar"
    ).innerHTML = `<img src="./static/image/S.PNG" alt="" />`;
    console.log(sign_text[1]);
    await delay(1000);
    if (n_class == 1) {
      face_stand += 1;
    } else {
      // face out of frame cicle
      face_stand = 0;
    }
    // Make sure face stand
    if (face_stand > 3) {
      break;
    }
  }

  for (const i in face_check_) {
    let face_mode = face_check_[i];
    let face_stand = 0;
    let count_ = 8;
    var status_process = true;

    // Send message, avatar S
    if (face_mode == 1) {
      document.getElementById("text-sign").innerHTML = "Please place your face in the center of the circle. for Take a photo"
    }
    else {
      document.getElementById("text-sign").innerHTML = sign_text[face_mode];
    }
    document.getElementById(
      "avatar"
    ).innerHTML = `<img src="./static/image/${face_class[face_mode]}.PNG" alt="" />`;
    console.log(sign_text[face_mode], face_mode);
    // Set for display message avatar, count together
    document.getElementById("text-time").innerHTML = `${count_}`;

    while (true) {
      // Send Countdown
      document.getElementById("text-time").innerHTML = `${count_}s`;
      console.log(count_);
      await delay(1000);
      if (n_class == face_mode) {
        face_stand += 1;
      }
      // Make sure face stand 2s and Take a photo if face_mode = 1
      if (face_stand > 2) {
        if (face_mode == 1) {
          capture();
        }
        
        break;
      }

      if (count_ < 1) {
        
        status_process = false;
        break;
      }
      count_ -= 1;
    }
    // if status false: break for next comand
    if (!status_process) {
      break;
    }
    document.getElementById("text-time").innerHTML = `${count_}`;
  }
    
  document.getElementById("page-d").style.zIndex = -3;
  document.getElementById("camera").style.display = -3;
  if (status_process) {
    document.getElementById(
      "sign-finish"
    ).innerHTML = `<img src="./static/image/complete.png" alt="" />`;
    document.getElementById("text-finish").innerHTML = `Complete!`;

    console.log("Complete");
  } else {
    document.getElementById(
      "sign-finish"
    ).innerHTML = `<img src="./static/image/wrong.png" alt="" />`;
    document.getElementById("text-finish").innerHTML = `Have something wrong!`;
    console.log("Have something wrong!");
  }
}

// ****************************************************************88
//Upload face card
const image_input_face = document.querySelector("#image_input_face");
let uploaded_image_face = "";
image_input_face.addEventListener("change", function () {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploaded_image_face = reader.result;
    document.querySelector(
      "#display_image_face"
    ).style.backgroundImage = `url(${uploaded_image_face})`;
  });
  reader.readAsDataURL(this.files[0]);
});

//Upload id card
const image_input_id = document.querySelector("#image_input_id");
let uploaded_image_id = "";
image_input_id.addEventListener("change", function () {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploaded_image_id = reader.result;
    document.querySelector(
      "#display_image_id"
    ).style.backgroundImage = `url(${uploaded_image_id})`;
  });
  reader.readAsDataURL(this.files[0]);
});


async function capture() {
  var canvas = document.createElement('canvas');
  var video = document.getElementsByClassName("input_video")[0];

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas
    .getContext("2d")
    .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

    const form_card = document.getElementById("image-card");
    let card_payload = new FormData(form_card);
    // console.log(card_payload)
    let imageBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
    console.log(imageBlob)
    // let imageBlob = canvas.toDataURL("image/png")
    card_payload.append('files', imageBlob, 'filename.png')

    const id_user = getCookieValue("id");
    console.log('Cookie:',id_user)
    console.log('Cookie raw:', document.cookie)
    let response = await fetch(`/uploads-verify/${id_user}`, {
        method: "POST",
        body: card_payload,
      })
    // let result = await response.json();
    // console.log(result.verify)

}

// GET COOKIE
function getCookieValue(cookieName) {
  const cookies = document.cookie.split("; ");
  for (let i = 0; i < cookies.length; i++) {
    const [name, value] = cookies[i].split("=");
    if (name === cookieName) {
      return value;
    }
  }
  return null; // Cookie not found
}