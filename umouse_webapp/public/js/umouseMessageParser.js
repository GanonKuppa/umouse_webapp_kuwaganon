function parseMouseX(intList) {
  let int_val = intList[92 + 1] + (intList[92] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let mouse_x = int_val / 1000.0;
  return mouse_x;
}

function parseMouseY(intList) {
  let int_val = intList[94 + 1] + (intList[94] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let mouse_y = int_val / 1000.0;
  return mouse_y;
}

function parseMouseAng(intList) {
  int_val = intList[96 + 1] + (intList[96] << 8);
  //if (int_val > 32767) int_val = int_val - 65536;
  mouse_ang = int_val / 100.0;
  return mouse_ang;
}

function parseMouseV(intList) {
  let int_val = intList[106 + 1] + (intList[106] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let mouse_v = int_val / 10000.0;
  return mouse_v;
}

function parseTargetX(intList) {
  let int_val = intList[100 + 1] + (intList[100] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let target_x = int_val / 1000.0;
  return target_x;
}

function parseTargetY(intList) {
  let int_val = intList[102 + 1] + (intList[102] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let target_y = int_val / 1000.0;
  return target_y;
}

function parseTargetAng(intList) {
  let int_val = intList[104 + 1] + (intList[104] << 8);
  let target_ang = int_val / 100.0;
  return target_ang;
}

function parseTargetV(intList) {
  let int_val = intList[110 + 1] + (intList[110] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let target_v = int_val / 10000.0;
  return target_v;
}

function parseVoltage(intList) {
  return 30.0 / 20.0 * ((intList[20] << 8) + intList[21]) * 3.2 / 4095;
}

function parseTime(intList) {
  return (intList[11] + (intList[10] << 8) + (intList[9] << 16) + (intList[8] << 24)) / 1000.0;
}

function parseWallL(intList) {
  return intList[62 + 1] + (intList[62] << 8);
}

function parseWallR(intList) {
  return intList[60 + 1] + (intList[60] << 8);
}

function parseWallRF(intList) {
  return intList[64 + 1] + (intList[64] << 8);
}

function parseWallLF(intList) {
  return intList[58 + 1] + (intList[58] << 8);
}

function parseVoltageR(intList){
  let int_val = intList[30+ 1] + (intList[30] << 8);
  if (int_val > 32767) int_val = int_val - 65536;
  let vol_r = int_val / 5000.0;
  return vol_r;
  
}

function parseVoltageL(intList){
  let int_val = intList[28 + 1] + (intList[28] << 8);
  if (int_val > 32767) int_val = int_val - 65536;

  let vol_l = int_val / 5000.0;
  return vol_l;

}

function parseLed_R(intList){
  let int_val = intList[66 + 1] + (intList[66] << 8);
  return int_val;
};

function parseLed_G(intList){
  let int_val = intList[68 + 1] + (intList[68] << 8);
  return int_val;
};

function parseLed_B(intList){
  let int_val = intList[70 + 1] + (intList[70] << 8);
  return int_val;
};


function parseTargetV_pos(intList){
  let int_val = intList[112 + 1] + (intList[112] << 8);
  if (int_val > 32767) int_val = int_val - 65536;

  let t_v_pos = int_val / 10000;
  return t_v_pos;
};


function parseEstiAngV(intList){
  let int_val = intList[114 + 1] + (intList[114] << 8);
  if (int_val > 32767) int_val = int_val - 65536;

  let esti_ang_v = int_val / 10;
  return esti_ang_v;
};

function parseTargetAngV(intList){
  let int_val = intList[116 + 1] + (intList[116] << 8);
  if (int_val > 32767) int_val = int_val - 65536;

  let target_ang_v = int_val / 10;
  return target_ang_v;
};

function parseTargetAngV_pos(intList){
  let int_val = intList[118 + 1] + (intList[118] << 8);
  if (int_val > 32767) int_val = int_val - 65536;

  let target_ang_v_pos = int_val / 10;
  return target_ang_v_pos;
};


