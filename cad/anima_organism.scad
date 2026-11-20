// ============================================================================
// ANIMA MODULAR BIO-ROBOTIC ORGANISM — PARAMETRIC 3D CAD SCRIPT (OpenSCAD)
// ============================================================================
// Watertight, manifold-ready parametric CAD for 3D printing (FDM/SLA) or CNC.
//
// 1-CLICK EXPORT (OpenSCAD Customizer or CLI):
//   - OpenSCAD GUI: Window -> Customizer -> select `export_part`, press F6
//     (Render), then File -> Export -> Export as STL (or 3MF).
//   - STEP Export: Open this .scad file in FreeCAD (OpenSCAD Workbench) and
//     export the rendered solid directly to STEP (.step/.stp).
//   - CLI Export:
//       openscad -o upper_link.stl -D 'export_part="upper_link"' anima_organism.scad
//
// Reference Component Dimensions:
//   - TowerPro MG996R:  pocket 42.0 x 21.0 x 38.0 mm, M3 ears 48.0 x 10.0 mm
//   - TowerPro MG90S:   pocket 24.0 x 13.5 x 20.0 mm
//   - 688ZZ Bearing:    16.0 mm OD, 5.0 mm thickness, 8.0 mm bore
//   - EMAX ES08MD II:   body 23.0 x 11.5 x 24.0 mm (pocket 23.6 x 12.1 x 20.0 mm)
//   - EMBEST CAM8200-U: 38.0 x 38.0 mm PCB, 28.0 x 28.0 mm M2 mounting pattern
// ============================================================================

/* [Export Selector] */
// Select a single part (oriented flat on Z=0 for fabrication) or full assembly
export_part = "assembly"; // [assembly, upper_link, lower_link, base_bracket, elbow_bracket, hub_plate, eye_gimbal, gimbal_pan_base, gimbal_tilt_clevis, gimbal_roll_clevis, gimbal_camera_cradle, print_plate_single_limb]

/* [Assembly Pose & Animation] */
// Number of modular limbs around the central hub (360 / 24 = 15 deg pitch)
num_limbs          = 24;
// Shoulder elevation angle (degrees) in assembly view
pose_shoulder_deg  = 22;
// Elbow flexion angle (degrees) in assembly view
pose_elbow_deg     = -38;
// Organic wave amplitude across the 24 limbs (0 = uniform pose)
pose_wave_amp_deg  = 10;
// Eye gimbal articulation angles (degrees)
gimbal_pan_deg     = 0;
gimbal_tilt_deg    = 12;
gimbal_roll_deg    = 0;

/* [Mesh Resolution & Boolean Hygiene] */
// Global curve smoothness (spec: $fn = 60)
$fn      = 60;
// Boolean overlap/penetration epsilon to prevent coplanar non-manifold faces
eps      = 0.05;
// Structural union overlap to guarantee single watertight manifold volumes
ovl      = 0.15;
// Standard edge chamfer/fillet size
chamfer  = 0.6;
// General mechanical print clearance
tol      = 0.25;

/* [1. Modular Two-Joint Limb Parameters] */
L_upper          = 120.0; // Upper link centre-to-centre between pivot holes (mm)
L_lower          = 100.0; // Lower link centre-to-centre (mm)
link_width       = 24.0;  // Link plate width (mm)
plate_thick      = 3.0;   // Link plate thickness (mm)
lower_tip_width  = 9.0;   // Tapered organic tip width on lower link (mm)

// Integrated longitudinal cable routing channel on upper link
cable_ch_w       = 6.0;   // Internal cable channel width (mm)
cable_ch_h       = 4.2;   // Channel wall height above plate (mm)
cable_ch_wall    = 1.6;   // Side wall thickness (mm)
snap_clip_len    = 7.0;   // Snap-clip longitudinal length (mm)
snap_clip_over   = 1.3;   // Overhang per side for cable retention (mm)
snap_clip_thick  = 1.2;   // Top snap-clip lip thickness (mm)

/* [2. Fastener & Bearing Parameters] */
d_m2             = 2.2;   // M2 clearance hole diameter (mm)
d_m2_tap         = 1.85;  // M2 self-tap / pilot hole diameter (mm)
d_m3             = 3.2;   // M3 clearance hole diameter (mm)
d_m3_cb          = 5.8;   // M3 socket head counterbore diameter (mm)
d_m6             = 6.4;   // M6 clearance hole diameter (mm)
d_m6_cb          = 10.5;  // M6 socket head counterbore diameter (mm)
d_tripod_insert  = 8.0;   // 1/4-20 brass heat-set threaded insert bore (mm)
d_tripod_clear   = 6.6;   // 1/4-20 through-clearance bore (mm)

// 688ZZ radial ball bearing
bearing_od       = 16.0;  // 688ZZ outer diameter (mm)
bearing_thick    = 5.0;   // 688ZZ thickness (mm)
bearing_bore     = 8.0;   // 688ZZ inner bore diameter (mm)
bearing_lip_id   = 12.6;  // Retaining shoulder ID (< 16 mm OD, > 8 mm bore)

/* [3. Servo Pocket Parameters] */
// TowerPro MG996R (Base Joint)
mg996r_l         = 42.0;  // Body pocket length (mm)
mg996r_w         = 21.0;  // Body pocket width (mm)
mg996r_d         = 38.0;  // Body pocket depth (mm)
mg996r_ear_dx    = 48.0;  // M3 ear screw spacing X (mm)
mg996r_ear_dy    = 10.0;  // M3 ear screw spacing Y (mm)
mg996r_wall      = 2.0;   // Tangential wall thickness (outer_w = 25 mm clears 24x pitch)
mg996r_shaft_off = 10.5;  // Output shaft offset from pocket centre along length

// TowerPro MG90S (Elbow Joint)
mg90s_l          = 24.0;  // Body pocket length (mm)
mg90s_w          = 13.5;  // Body pocket width (mm)
mg90s_d          = 20.0;  // Body pocket depth (mm)
mg90s_ear_dx     = 28.0;  // MG90S ear screw spacing (mm)
mg90s_wall       = 2.8;   // Elbow bracket housing wall thickness (mm)
mg90s_shaft_off  = 6.0;   // Output shaft offset from pocket centre along length

// EMAX ES08MD II (3-Axis Camera Eye Gimbal)
// Body spec: 23.0 x 11.5 x 24.0 mm; pocket includes 0.6 mm print clearance
es08_l           = 23.6;  // Body pocket length (mm)
es08_w           = 12.1;  // Body pocket width (mm)
es08_d           = 20.0;  // Body pocket depth (mm)
es08_ear_dx      = 28.0;  // Ear mounting hole spacing (mm)
es08_wall        = 2.4;   // Gimbal clevis wall thickness (mm)
es08_shaft_off   = 5.8;   // Output spline offset from pocket centre

/* [4. Central Hub Chassis Parameters] */
hub_dia          = 260.0; // Central rigid plate diameter (mm)
hub_thick        = 6.0;   // Central rigid plate thickness (mm)
hub_slot_r       = 114.0; // Radial centre of the 24 limb mounting slots (mm)
hub_slot_l       = 18.0;  // Radial length of each mounting slot (mm)
hub_slot_w       = 7.0;   // Tangential width of each mounting slot (mm)
// Shared M3 bolt pattern between hub_plate() and base_bracket() (fits 25 mm width)
hub_bolt_dx      = 22.0;  // Radial spacing of M3 base bolts around slot (mm)
hub_bolt_dy      = 15.0;  // Tangential spacing of M3 base bolts around slot (mm)
hub_boss_od      = 78.0;  // Reinforced central stand interface boss OD (mm)
hub_boss_h       = 16.0;  // Total reinforced boss height (mm)
hub_m6_bcd       = 54.0;  // 4x M6 bolt circle diameter (mm)
hub_tripod_fl_d  = 34.0;  // 1/4-20 tripod flange recess diameter (mm)
hub_tripod_fl_h  = 3.0;   // 1/4-20 tripod flange recess depth (mm)
hub_wire_ring_r  = 74.0;  // Radius for 24 dual-bundle limb wire cutouts (mm)
hub_bay_wall_od  = 122.0; // Central electronics bay ring outer diameter (mm)
hub_bay_wall_id  = 114.0; // Central electronics bay ring inner diameter (mm)
hub_bay_wall_h   = 12.0;  // Electronics bay collar height above plate (mm)

/* [5. 3-Axis Camera Eye Gimbal & EMBEST CAM8200-U Parameters] */
cam_pcb_size     = 38.0;  // EMBEST CAM8200-U PCB width & height (38 x 38 mm)
cam_pcb_tol      = 0.5;   // PCB pocket clearance (mm)
cam_hole_spacing = 28.0;  // 28 x 28 mm M2 mounting hole pattern (mm)
cam_lens_dia     = 18.0;  // Forward camera lens clearance aperture (mm)
cam_cradle_wall  = 3.0;   // Camera cradle perimeter wall thickness (mm)
cam_cradle_depth = 12.0;  // Camera cradle housing depth (mm)
usb_cable_dia    = 4.6;   // Rear USB cable OD for strain relief collar (mm)
usb_collar_len   = 14.0;  // Rear strain relief collar length (mm)


// ============================================================================
// UTILITY PRIMITIVES (Fast, Watertight, Chamfered/Filleted Geometry)
// ============================================================================

// Beveled cylinder with clean top and bottom chamfers (manifold, no minkowski lag)
module beveled_cylinder(r, h, b = chamfer) {
    bb = min(b, h / 3, r / 3);
    union() {
        cylinder(r1 = r - bb, r2 = r, h = bb + eps);
        translate([0, 0, bb])
            cylinder(r = r, h = h - 2 * bb);
        translate([0, 0, h - bb - eps])
            cylinder(r1 = r, r2 = r - bb, h = bb + eps);
    }
}

// 2D rounded rectangle centered on X and Y
module rounded_rect_2d(w, d, r = 2.0) {
    rr = min(r, w / 2 - 0.01, d / 2 - 0.01);
    offset(r = rr)
        square([w - 2 * rr, d - 2 * rr], center = true);
}

// 3D rounded box centered on X and Y, sitting on Z = 0..h, with optional Z chamfers
module rounded_box(w, d, h, r = 2.0, b = chamfer) {
    rr = min(r, w / 2 - 0.05, d / 2 - 0.05);
    bb = min(b, h / 3, rr * 0.7);
    if (bb > 0.05) {
        hull() {
            translate([0, 0, bb])
                linear_extrude(height = h - 2 * bb)
                    rounded_rect_2d(w, d, rr);
            linear_extrude(height = h)
                rounded_rect_2d(w - 2 * bb, d - 2 * bb, max(0.2, rr - bb));
        }
    } else {
        linear_extrude(height = h)
            rounded_rect_2d(w, d, rr);
    }
}

// Stadium (obround slot) 2D shape centered at origin, aligned along X
module stadium_2d(length, width) {
    r = width / 2;
    span = max(0.01, length - width);
    hull() {
        translate([-span / 2, 0]) circle(r = r);
        translate([ span / 2, 0]) circle(r = r);
    }
}

// Counterbored through-hole along Z (starts at z_bottom, counterbore on top)
module cb_hole(d_thru, d_cb, h_total, h_cb) {
    translate([0, 0, -eps])
        cylinder(d = d_thru, h = h_total + 2 * eps);
    translate([0, 0, h_total - h_cb])
        cylinder(d = d_cb, h = h_cb + eps);
}

// Servo horn radial bolt pattern (4 holes on a given bolt circle diameter)
module horn_bolt_pattern(bcd = 14.0, d_hole = d_m3, h = 10.0, count = 4) {
    for (a = [0 : count - 1]) {
        rotate([0, 0, a * (360 / count) + 45])
            translate([bcd / 2, 0, -eps])
                cylinder(d = d_hole, h = h + 2 * eps);
    }
}


// ============================================================================
// MODULE 1: upper_link()
// ============================================================================
// 120 mm centre-to-centre between pivot holes, 24 mm width, 3 mm thickness.
// Includes 6 mm integrated longitudinal cable routing channel with snap-clips.
// Local origin: Base pivot centre at (0, 0, 0); elbow pivot at (L_upper, 0, 0).
module upper_link() {
    r_end      = link_width / 2;
    ch_start   = 17.0;
    ch_end     = L_upper - 17.0;
    ch_len     = ch_end - ch_start;
    ch_outer_w = cable_ch_w + 2 * cable_ch_wall;
    num_clips  = 4;

    difference() {
        union() {
            // Main structural plate with rounded ends and chamfered edges
            hull() {
                beveled_cylinder(r = r_end, h = plate_thick, b = chamfer);
                translate([L_upper, 0, 0])
                    beveled_cylinder(r = r_end, h = plate_thick, b = chamfer);
            }

            // Reinforced pivot bosses (1.2 mm shoulder around both pivots)
            translate([0, 0, plate_thick - ovl])
                beveled_cylinder(r = 9.5, h = 1.2 + ovl, b = 0.35);
            translate([L_upper, 0, plate_thick - ovl])
                beveled_cylinder(r = 8.5, h = 1.2 + ovl, b = 0.35);

            // Integrated 6 mm longitudinal cable routing channel walls
            for (side = [-1, 1]) {
                y_wall = side * (cable_ch_w / 2 + cable_ch_wall / 2);
                translate([ch_start + ch_len / 2, y_wall, plate_thick - ovl])
                    rounded_box(ch_len, cable_ch_wall, cable_ch_h + ovl, r = 0.6, b = 0.25);
            }

            // Staggered snap-clips along the 6 mm cable routing channel
            for (i = [0 : num_clips - 1]) {
                x_clip = ch_start + (i + 0.5) * (ch_len / num_clips);
                for (side = [-1, 1]) {
                    x_stagger = x_clip + side * (snap_clip_len * 0.55);
                    if (x_stagger > ch_start + snap_clip_len / 2 && x_stagger < ch_end - snap_clip_len / 2) {
                        translate([
                            x_stagger,
                            side * (cable_ch_w / 2 + cable_ch_wall / 2 - snap_clip_over / 2),
                            plate_thick + cable_ch_h - snap_clip_thick - ovl
                        ])
                            rounded_box(
                                snap_clip_len,
                                cable_ch_wall + snap_clip_over,
                                snap_clip_thick + ovl,
                                r = 0.4,
                                b = 0.2
                            );
                    }
                }
            }
        }

        // Base pivot bore (8 mm 688ZZ shaft / MG996R horn hub)
        translate([0, 0, -eps])
            cylinder(d = bearing_bore + tol, h = plate_thick + 3.0);

        // Base pivot M3 servo horn mounting ring (15 mm BCD)
        horn_bolt_pattern(bcd = 15.0, d_hole = d_m3, h = plate_thick + 3.0, count = 4);

        // Elbow pivot bore (M3 central fastener / pivot alignment)
        translate([L_upper, 0, -eps])
            cylinder(d = d_m3, h = plate_thick + 3.0);

        // Elbow bracket M3 mounting holes (14 mm BCD, 4x)
        translate([L_upper, 0, 0])
            horn_bolt_pattern(bcd = 14.0, d_hole = d_m3, h = plate_thick + 3.0, count = 4);

        // Weight-reduction flanking slots outside the 6 mm cable channel
        for (side = [-1, 1]) {
            y_slot = side * (ch_outer_w / 2 + 4.2);
            for (seg = [0 : 1]) {
                x_seg = 36.0 + seg * 48.0;
                translate([x_seg, y_slot, -eps])
                    linear_extrude(height = plate_thick + 2 * eps)
                        stadium_2d(32.0, 3.4);
            }
        }
    }
}


// ============================================================================
// MODULE 2: lower_link()
// ============================================================================
// 100 mm centre-to-centre, 24 mm width at pivot, 3 mm thickness, with a
// tapered organic tip and stiffening dorsal rib.
// Local origin: Elbow pivot centre at (0, 0, 0); organic tip pivot at (L_lower, 0, 0).
module lower_link() {
    r_base = link_width / 2;
    r_tip  = lower_tip_width / 2;

    difference() {
        union() {
            // Smoothly tapered organic blade profile (two-stage hull for bio-taper)
            hull() {
                beveled_cylinder(r = r_base, h = plate_thick, b = chamfer);
                translate([L_lower * 0.45, 0, 0])
                    beveled_cylinder(r = r_base * 0.72, h = plate_thick, b = chamfer);
            }
            hull() {
                translate([L_lower * 0.45, 0, 0])
                    beveled_cylinder(r = r_base * 0.72, h = plate_thick, b = chamfer);
                translate([L_lower, 0, 0])
                    beveled_cylinder(r = r_tip, h = plate_thick, b = chamfer);
            }

            // Organic dorsal spine rib tapering toward the tip for flexural stiffness
            hull() {
                translate([15.0, 0, plate_thick - ovl])
                    beveled_cylinder(r = 2.6, h = 2.4 + ovl, b = 0.5);
                translate([L_lower - 8.0, 0, plate_thick - ovl])
                    beveled_cylinder(r = 1.3, h = 1.2 + ovl, b = 0.35);
            }

            // Reinforced elbow horn boss
            translate([0, 0, plate_thick - ovl])
                beveled_cylinder(r = 8.5, h = 1.2 + ovl, b = 0.35);
        }

        // Elbow pivot central bore (M3 pivot screw)
        translate([0, 0, -eps])
            cylinder(d = d_m3, h = plate_thick + 3.0);

        // MG90S servo horn M3 fastener pattern (12 mm BCD, 4x)
        horn_bolt_pattern(bcd = 12.0, d_hole = d_m3, h = plate_thick + 3.0, count = 4);

        // Tip reference eyelet at exact 100 mm centre-to-centre (M3 sensor/tendon eye)
        translate([L_lower, 0, -eps])
            cylinder(d = d_m3, h = plate_thick + 3.0);

        // Organic lightening fenestrations flanking the central spine
        for (side = [-1, 1]) {
            translate([30.0, side * 5.8, -eps])
                rotate([0, 0, -side * 5.5])
                    linear_extrude(height = plate_thick + 2 * eps)
                        stadium_2d(22.0, 3.2);
            translate([60.0, side * 4.2, -eps])
                rotate([0, 0, -side * 4.5])
                    linear_extrude(height = plate_thick + 2 * eps)
                        stadium_2d(18.0, 2.4);
        }
    }
}


// ============================================================================
// MODULE 3: base_bracket()
// ============================================================================
// Houses TowerPro MG996R servo (pocket 42 x 21 x 38 mm deep), M3 ear holes
// (48 x 10 mm spacing), and coaxial 688ZZ bearing pocket (16 mm OD, 5 mm thick,
// 8 mm bore) to support radial pivot loads.
// Tangential envelope kept at 25.0 mm so all 24 brackets clear each other cleanly
// around the 260 mm hub_plate() at 15-degree increments.
// Local origin: Bottom mounting face at Z = 0, centred on hub radial slot.
module base_bracket() {
    outer_l      = mg996r_l + 2 * 7.5;        // 57.0 mm (accommodates 48 mm M3 ears)
    outer_w      = mg996r_w + 2 * mg996r_wall;// 25.0 mm (zero tangential interference)
    body_h       = mg996r_d + 4.0;            // 42.0 mm (38 mm pocket + 4 mm floor)
    servo_x_off  = 12.0;                      // Shifts servo outward so pocket clears r=99mm
    shaft_x      = servo_x_off + mg996r_shaft_off; // Output shaft radial position
    yoke_gap     = plate_thick + 3.0;         // Clearance for upper_link + horn
    yoke_arm_t   = bearing_thick + 2.5;       // 7.5 mm yoke (5 mm bearing + 2.5 mm lip)
    riser_x      = servo_x_off + outer_l / 2 - 4.0; // Outer radial riser (zero Y overhang)

    difference() {
        union() {
            // Base mounting flange seated directly over hub_plate() radial slot
            rounded_box(hub_bolt_dx + 10.0, outer_w, 5.0, r = 2.5, b = chamfer);

            // Keyed tenon on underside to locate cleanly into hub_plate() radial slot
            translate([0, 0, -hub_thick + 0.5])
                rounded_box(hub_slot_l - tol, hub_slot_w - tol, hub_thick - 0.5 + ovl, r = 1.5, b = 0.3);

            // Main MG996R servo housing block (shifted slightly outward along +X)
            translate([servo_x_off, 0, 0])
                rounded_box(outer_l, outer_w, body_h, r = 2.5, b = chamfer);

            // Outer radial riser column (stays inside 25 mm tangential width)
            translate([riser_x, 0, body_h - 10.0])
                rounded_box(8.0, outer_w, 10.0 + yoke_gap + yoke_arm_t, r = 2.0, b = chamfer);

            // Upper 688ZZ bearing yoke arm cantilevered inward over the output shaft axis
            hull() {
                translate([riser_x, 0, body_h + yoke_gap])
                    rounded_box(8.0, outer_w, yoke_arm_t, r = 2.0, b = chamfer);
                translate([shaft_x, 0, body_h + yoke_gap])
                    beveled_cylinder(r = bearing_od / 2 + 4.0, h = yoke_arm_t, b = chamfer);
            }
        }

        // TowerPro MG996R body pocket (42 x 21 x 38 mm deep, opening upward)
        translate([servo_x_off, 0, body_h - mg996r_d])
            rounded_box(mg996r_l, mg996r_w, mg996r_d + eps, r = 0.8, b = 0);

        // MG996R M3 mounting ear holes (exact 48 mm x 10 mm spacing)
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([
                servo_x_off + sx * (mg996r_ear_dx / 2),
                sy * (mg996r_ear_dy / 2),
                body_h - 14.0
            ])
                cylinder(d = d_m3, h = 14.0 + eps);
        }

        // Servo wire exit slot at inner rear of MG996R pocket toward hub wire ring
        translate([servo_x_off - mg996r_l / 2 - 4.0, 0, 5.0])
            rounded_box(12.0, 8.0, 10.0, r = 1.5, b = 0);

        // 688ZZ bearing pocket (16 mm OD, 5 mm thickness, 8 mm bore)
        // Bearing seats from the underside of the yoke arm against a 2.5 mm top lip
        translate([shaft_x, 0, body_h + yoke_gap - eps])
            cylinder(d = bearing_od + tol * 0.6, h = bearing_thick + eps);
        // Through-bore for 8 mm pivot shaft + retaining shoulder (12.6 mm ID)
        translate([shaft_x, 0, body_h + yoke_gap - eps])
            cylinder(d = bearing_lip_id, h = yoke_arm_t + 2 * eps);

        // 4x M3 base mounting holes (exact match to hub_plate() shared parameters)
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([sx * (hub_bolt_dx / 2), sy * (hub_bolt_dy / 2), -eps])
                cylinder(d = d_m3, h = 12.0);
        }
    }
}


// ============================================================================
// MODULE 4: elbow_bracket()
// ============================================================================
// Houses TowerPro MG90S micro servo (pocket 24 x 13.5 x 20 mm deep) with M3
// pivot horn fastener holes to couple upper_link() and lower_link().
// Local origin: Mounting interface to upper_link() at Z = 0, pivot axis at X = 0.
module elbow_bracket() {
    outer_l  = mg90s_l + 2 * 5.2;        // 34.4 mm (fits 28 mm MG90S ear holes)
    outer_w  = mg90s_w + 2 * mg90s_wall; // 19.1 mm
    body_h   = mg90s_d + 3.5;            // 23.5 mm (20 mm pocket + 3.5 mm floor)
    flange_t = 3.5;

    difference() {
        union() {
            // Base mounting flange coupling to upper_link() distal end (14 mm BCD M3)
            beveled_cylinder(r = link_width / 2, h = flange_t, b = chamfer);

            // MG90S servo housing block offset so output shaft aligns at X = 0, Y = 0
            translate([-mg90s_shaft_off, 0, flange_t - ovl])
                rounded_box(outer_l, outer_w, body_h + ovl, r = 2.4, b = chamfer);

            // Opposing pivot support ear (mini-clevis) stabilizing lower_link()
            translate([0, -(outer_w / 2 + 2.0), flange_t + body_h - 6.0])
                rounded_box(12.0, 5.0, 6.0 + plate_thick + 4.0, r = 1.5, b = 0.4);
            hull() {
                translate([0, -(outer_w / 2 + 2.0), flange_t + body_h + plate_thick + 1.2])
                    rounded_box(12.0, 5.0, 2.8, r = 1.2, b = 0.3);
                translate([0, 0, flange_t + body_h + plate_thick + 1.2])
                    beveled_cylinder(r = 5.5, h = 2.8, b = 0.3);
            }
        }

        // TowerPro MG90S body pocket (24 x 13.5 x 20 mm deep)
        translate([-mg90s_shaft_off, 0, flange_t + body_h - mg90s_d])
            rounded_box(mg90s_l, mg90s_w, mg90s_d + eps, r = 0.6, b = 0);

        // MG90S servo ear mounting holes (28 mm spacing, M2.2)
        for (sx = [-1, 1]) {
            translate([-mg90s_shaft_off + sx * (mg90s_ear_dx / 2), 0, flange_t + body_h - 10.0])
                cylinder(d = d_m2, h = 10.0 + eps);
        }

        // M3 pivot horn fastener holes on base flange (14 mm BCD, 4x) + central M3 bore
        translate([0, 0, -eps])
            cylinder(d = d_m3, h = flange_t + 4.0);
        horn_bolt_pattern(bcd = 14.0, d_hole = d_m3, h = flange_t + 4.0, count = 4);

        // Opposing M3 pivot screw hole in upper clevis tab
        translate([0, 0, flange_t + body_h + plate_thick + 1.0 - eps])
            cylinder(d = d_m3, h = 3.5);

        // Rear cable exit slot feeding into upper_link() 6 mm cable channel
        translate([-mg90s_shaft_off - mg90s_l / 2 - 2.5, 0, flange_t + 3.0])
            rounded_box(8.0, 6.0, 7.0, r = 1.0, b = 0);
    }
}


// ============================================================================
// MODULE 5: hub_plate()
// ============================================================================
// Central rigid plate (260 mm OD, 6 mm thick) with:
//   - 24 radial mounting slots at 15-degree increments + M3 fastener pairs
//   - Reinforced central stand boss with 4x M6 bolt circle & 1/4-20 tripod flange
//   - Internal routing cutouts for all 51 servo wire bundles (24x2 limb + 3 eye)
// Local origin: Bottom surface of main plate at Z = 0, centred on Z axis.
module hub_plate() {
    boss_z_bot = -(hub_boss_h - hub_thick); // Boss extends below plate for stand mount

    difference() {
        union() {
            // Main 260 mm diameter, 6 mm thick rigid chassis plate
            beveled_cylinder(r = hub_dia / 2, h = hub_thick, b = chamfer);

            // Reinforced central stand interface boss (underside + proud top collar)
            translate([0, 0, boss_z_bot])
                beveled_cylinder(r = hub_boss_od / 2, h = hub_boss_h + 4.0, b = 1.0);

            // 8 radial stiffening gussets tying central boss into the main plate
            for (g = [0 : 7]) {
                rotate([0, 0, g * 45 + 22.5])
                    translate([hub_boss_od / 2 + 12.0, 0, boss_z_bot + 3.0])
                        rounded_box(28.0, 4.0, hub_boss_h - hub_thick - 2.5 + ovl, r = 1.0, b = 0.3);
            }

            // Central electronics bay perimeter retaining ring on top face
            translate([0, 0, hub_thick - ovl])
                difference() {
                    beveled_cylinder(r = hub_bay_wall_od / 2, h = hub_bay_wall_h + ovl, b = 0.5);
                    translate([0, 0, -eps])
                        cylinder(r = hub_bay_wall_id / 2, h = hub_bay_wall_h + ovl + 2 * eps);
                }
        }

        // 24 radial mounting slots at exact 15-degree increments + flanking M3 holes
        for (i = [0 : num_limbs - 1]) {
            rotate([0, 0, i * (360 / num_limbs)]) {
                // Radial alignment slot for base_bracket() tenon
                translate([hub_slot_r, 0, -eps])
                    linear_extrude(height = hub_thick + 2 * eps)
                        stadium_2d(hub_slot_l, hub_slot_w);

                // 4x M3 mounting holes matching base_bracket() shared parameters
                for (sx = [-1, 1], sy = [-1, 1]) {
                    translate([
                        hub_slot_r + sx * (hub_bolt_dx / 2),
                        sy * (hub_bolt_dy / 2),
                        -eps
                    ])
                        cylinder(d = d_m3, h = hub_thick + 2 * eps);
                }

                // 24 radial wire routing cutouts (each carries 2 limb servo bundles = 48 bundles)
                translate([hub_wire_ring_r, 0, -eps])
                    linear_extrude(height = hub_thick + 2 * eps)
                        stadium_2d(14.0, 6.5);

                // Wire pass-through notches in electronics bay wall aligned with each limb
                translate([hub_bay_wall_od / 2 - 2.0, 0, hub_thick + 3.5])
                    rounded_box(10.0, 5.5, hub_bay_wall_h, r = 1.0, b = 0);
            }
        }

        // 3 dedicated eye-gimbal servo wire routing cutouts (48 + 3 = 51 total bundles)
        for (k = [0 : 2]) {
            rotate([0, 0, k * 120 + 30])
                translate([hub_m6_bcd / 2 + 12.0, 0, boss_z_bot - eps])
                    linear_extrude(height = hub_boss_h + 10.0)
                        stadium_2d(9.0, 5.2);
        }

        // 4x M6 bolt circle on central stand interface boss (with top counterbores)
        for (b = [0 : 3]) {
            rotate([0, 0, b * 90 + 45])
                translate([hub_m6_bcd / 2, 0, boss_z_bot])
                    cb_hole(d_m6, d_m6_cb, hub_boss_h + 4.0, 5.5);
        }

        // 1/4-20 tripod flange adapter interface at dead centre
        // Underside circular tripod flange recess
        translate([0, 0, boss_z_bot - eps])
            cylinder(d = hub_tripod_fl_d, h = hub_tripod_fl_h + eps);
        // Heat-set 1/4-20 brass threaded insert bore
        translate([0, 0, boss_z_bot + hub_tripod_fl_h - eps])
            cylinder(d = d_tripod_insert, h = 11.0);
        // Through-clearance bore into central bay
        translate([0, 0, boss_z_bot - eps])
            cylinder(d = d_tripod_clear, h = hub_boss_h + 6.0);

        // 4x M3 mounting holes on top of central boss for eye_gimbal() pedestal
        for (g = [0 : 3]) {
            rotate([0, 0, g * 90])
                translate([22.0, 0, hub_thick - 2.0])
                    cylinder(d = d_m3, h = 10.0);
        }
    }
}


// ============================================================================
// MODULE 6: 3-AXIS CAMERA EYE GIMBAL SUB-COMPONENTS & eye_gimbal()
// ============================================================================
// 3 miniature interlocking clevis brackets driven by 3x EMAX ES08MD II servos
// (Pan, Tilt, Roll), forward EMBEST CAM8200-U camera cradle (38x38 mm PCB,
// 28x28 mm M2 mounting holes), and rear USB cable strain relief collar.

// 6A. Pan Base Bracket (houses Pan EMAX ES08MD II vertically, bolts to hub boss)
module gimbal_pan_base() {
    base_d = 52.0;
    base_h = 4.0;
    hous_l = es08_l + 2 * 5.0;       // 33.6 mm (fits 28 mm ear spacing)
    hous_w = es08_w + 2 * es08_wall; // 16.9 mm
    hous_h = es08_d + 3.0;           // 23.0 mm

    difference() {
        union() {
            beveled_cylinder(r = base_d / 2, h = base_h, b = chamfer);
            translate([-es08_shaft_off, 0, base_h - ovl])
                rounded_box(hous_l, hous_w, hous_h + ovl, r = 2.0, b = chamfer);
        }

        // Pan EMAX ES08MD II pocket (output shaft centered at X=0, Y=0)
        translate([-es08_shaft_off, 0, base_h + hous_h - es08_d])
            rounded_box(es08_l, es08_w, es08_d + eps, r = 0.5, b = 0);

        // Servo ear screw holes (28 mm spacing, M2)
        for (sx = [-1, 1]) {
            translate([-es08_shaft_off + sx * (es08_ear_dx / 2), 0, base_h + hous_h - 10.0])
                cylinder(d = d_m2, h = 10.0 + eps);
        }

        // Hub pedestal mounting holes (4x M3 on 44 mm BCD)
        for (g = [0 : 3]) {
            rotate([0, 0, g * 90])
                translate([22.0, 0, -eps])
                    cylinder(d = d_m3, h = base_h + 2 * eps);
        }

        // Central cable pass-through
        translate([-es08_shaft_off - es08_l / 2 - 2.0, 0, base_h + 2.0])
            rounded_box(8.0, 6.0, 6.0, r = 1.0, b = 0);
    }
}

// 6B. Tilt Clevis Bracket (interlocking U-clevis driven by Pan horn, holds Tilt ES08MD II)
module gimbal_tilt_clevis() {
    span_y = 46.0; // Inner clearance for Roll clevis + camera width
    arm_h  = 34.0;
    base_t = 3.5;
    arm_t  = 3.2;
    hous_l = es08_l + 2 * 5.0;
    hous_w = es08_w + 2 * es08_wall;

    difference() {
        union() {
            // Bottom bridge coupling to Pan servo horn
            rounded_box(22.0, span_y + 2 * arm_t, base_t, r = 2.5, b = chamfer);

            // Right arm (passive pivot pin side)
            translate([0, -(span_y / 2 + arm_t / 2), base_t - ovl])
                rounded_box(18.0, arm_t, arm_h + ovl, r = 2.0, b = 0.4);

            // Left arm (houses Tilt EMAX ES08MD II servo horizontally)
            translate([0, (span_y / 2 + arm_t / 2), base_t - ovl])
                rounded_box(20.0, arm_t, arm_h + ovl, r = 2.0, b = 0.4);
            // Symmetric housing centered on the Tilt pocket at X = es08_shaft_off
            translate([es08_shaft_off, span_y / 2 + arm_t + es08_d / 2 - 2.0, arm_h - 2.0])
                rotate([90, 0, 0])
                    rounded_box(hous_l, hous_w, es08_d + 3.0, r = 2.0, b = 0.4);
        }

        // Pan horn M2 mounting pattern on bottom bridge
        translate([0, 0, -eps])
            cylinder(d = d_m3, h = base_t + 2 * eps);
        horn_bolt_pattern(bcd = 12.0, d_hole = d_m2, h = base_t + 2 * eps, count = 4);

        // Tilt EMAX ES08MD II pocket on left arm (shaft centered at X=0, Z=arm_h-2)
        translate([es08_shaft_off, span_y / 2 + arm_t + es08_d / 2 - 2.0, arm_h - 2.0])
            rotate([90, 0, 0])
                rounded_box(es08_l, es08_w, es08_d + 6.0, r = 0.5, b = 0);

        // Tilt servo ear screw holes (28 mm spacing)
        for (sx = [-1, 1]) {
            translate([es08_shaft_off + sx * (es08_ear_dx / 2), span_y / 2 - eps, arm_h - 2.0])
                rotate([-90, 0, 0])
                    cylinder(d = d_m2, h = 14.0);
        }

        // Opposing passive Tilt pivot bore on right arm (M3 shoulder screw)
        translate([0, -(span_y / 2 + arm_t + eps), arm_h - 2.0])
            rotate([-90, 0, 0])
                cylinder(d = d_m3, h = arm_t + 2 * eps);
    }
}

// 6C. Roll Clevis Bracket (interlocking inner clevis driven by Tilt horn, holds Roll ES08MD II)
module gimbal_roll_clevis() {
    inner_y = 43.0; // Fits snugly inside Tilt clevis (46 mm)
    rear_x  = 22.0; // Offset behind optical pivot for Roll servo
    arm_t   = 3.0;
    hous_l  = es08_l + 2 * 5.0;
    hous_w  = es08_w + 2 * es08_wall;

    difference() {
        union() {
            // Left & right side arms connecting Tilt pivot axis to rear Roll servo bridge
            for (sy = [-1, 1]) {
                translate([-rear_x / 2, sy * (inner_y / 2 - arm_t / 2), 0])
                    rounded_box(rear_x + 12.0, arm_t, 14.0, r = 2.0, b = 0.35);
            }

            // Rear transverse bridge + Roll EMAX ES08MD II housing (axis along +X)
            translate([-rear_x, 0, 0])
                rounded_box(es08_d + 3.0, inner_y, hous_w + 2.0, r = 2.0, b = 0.4);
            translate([-rear_x, -es08_shaft_off, 0])
                rounded_box(es08_d + 3.0, hous_l, hous_w + 2.0, r = 2.0, b = 0.4);
        }

        // Tilt pivot holes on both side arms (X=0, Z=7)
        translate([0, -(inner_y / 2 + eps), 7.0])
            rotate([-90, 0, 0])
                cylinder(d = d_m3, h = inner_y + 2 * eps);

        // Roll EMAX ES08MD II pocket (facing +X toward camera cradle, shaft at Y=0)
        translate([-rear_x + 2.0, -es08_shaft_off, (hous_w + 2.0) / 2])
            rotate([0, 90, 0])
                rounded_box(es08_w, es08_l, es08_d + 4.0, r = 0.5, b = 0);

        // Roll servo ear screw holes (28 mm spacing along Y)
        for (sy = [-1, 1]) {
            translate([-rear_x - 2.0, -es08_shaft_off + sy * (es08_ear_dx / 2), (hous_w + 2.0) / 2])
                rotate([0, 90, 0])
                    cylinder(d = d_m2, h = es08_d + 10.0);
        }
    }
}

// 6D. Forward Camera Cradle (EMBEST CAM8200-U 38x38 mm PCB, 28x28 mm M2, rear USB strain relief)
module gimbal_camera_cradle() {
    outer_sz = cam_pcb_size + 2 * cam_cradle_wall; // 44.0 x 44.0 mm
    back_t   = 3.2;

    difference() {
        union() {
            // Main forward camera bezel/cradle housing (optical axis along +Z locally)
            rounded_box(outer_sz, outer_sz, cam_cradle_depth, r = 3.5, b = chamfer);

            // 4 internal PCB corner standoffs (28 x 28 mm M2 pattern)
            for (sx = [-1, 1], sy = [-1, 1]) {
                translate([sx * (cam_hole_spacing / 2), sy * (cam_hole_spacing / 2), back_t - ovl])
                    cylinder(d = 5.5, h = 3.5 + ovl);
            }

            // Rear USB camera cable strain relief collar (flared saddle below Z = 0)
            translate([0, -10.0, -usb_collar_len + ovl])
                beveled_cylinder(r = usb_cable_dia / 2 + 3.2, h = usb_collar_len, b = 0.8);
            // Flared bell-mouth lip at rear of strain relief
            translate([0, -10.0, -usb_collar_len])
                cylinder(r1 = usb_cable_dia / 2 + 4.2, r2 = usb_cable_dia / 2 + 3.0, h = 2.5);
        }

        // EMBEST CAM8200-U 38 x 38 mm PCB pocket (recessed from front face)
        translate([0, 0, back_t])
            rounded_box(
                cam_pcb_size + cam_pcb_tol,
                cam_pcb_size + cam_pcb_tol,
                cam_cradle_depth - back_t + eps,
                r = 1.2,
                b = 0
            );

        // 4x M2 camera PCB mounting holes (exact 28 x 28 mm spacing)
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([sx * (cam_hole_spacing / 2), sy * (cam_hole_spacing / 2), -eps])
                cylinder(d = d_m2, h = cam_cradle_depth + 2 * eps);
        }

        // Roll servo horn mounting interface at centre of rear wall (12 mm BCD, M2)
        translate([0, 0, -eps])
            cylinder(d = d_m3, h = back_t + 2 * eps);
        horn_bolt_pattern(bcd = 12.0, d_hole = d_m2, h = back_t + 2 * eps, count = 4);

        // USB cable through-bore in rear strain relief collar + split flex-relief slot
        translate([0, -10.0, -usb_collar_len - eps])
            cylinder(d = usb_cable_dia + tol, h = usb_collar_len + back_t + 2 * eps);
        // Side entry/flex slot on strain relief collar
        translate([0, -10.0 - (usb_cable_dia / 2 + 2.0), -usb_collar_len - eps])
            rounded_box(2.2, 6.0, usb_collar_len - 2.0, r = 0.4, b = 0);
        // Zip-tie retention groove around collar midpoint (non-coplanar inner cutter)
        translate([0, -10.0, -usb_collar_len / 2 - 1.5])
            difference() {
                cylinder(r = usb_cable_dia / 2 + 4.5, h = 3.0);
                translate([0, 0, -eps])
                    cylinder(r = usb_cable_dia / 2 + 2.2, h = 3.0 + 2 * eps);
            }
    }
}

// Complete assembled 3-Axis Camera Eye Gimbal
module eye_gimbal(pan = gimbal_pan_deg, tilt = gimbal_tilt_deg, roll = gimbal_roll_deg) {
    // 1. Fixed Pan base
    color("SlateGray")
        gimbal_pan_base();

    // 2. Pan rotation stage -> Tilt clevis
    translate([0, 0, 29.0])
        rotate([0, 0, pan]) {
            color("SteelBlue")
                gimbal_tilt_clevis();

            // 3. Tilt rotation stage -> Roll clevis
            translate([0, 0, 32.0])
                rotate([0, tilt, 0]) {
                    translate([0, 0, -7.0])
                        color("DarkSlateGray")
                            gimbal_roll_clevis();

                    // 4. Roll rotation stage -> Forward EMBEST CAM8200-U camera cradle
                    translate([12.0, 0, 0])
                        rotate([roll, 0, 0])
                            rotate([0, 90, 0])
                                color("Crimson")
                                    gimbal_camera_cradle();
                }
        }
}


// ============================================================================
// MODULE 7: full_24_limb_assembly()
// ============================================================================
// Assembles the central 260 mm hub_plate(), 24 radial modular limbs spaced at
// 15-degree increments (base_bracket + upper_link + elbow_bracket + lower_link),
// and the 3-axis eye_gimbal() mounted at the central dorsal apex.
module single_limb_assembled(shoulder_ang = pose_shoulder_deg, elbow_ang = pose_elbow_deg) {
    // Base joint bracket seated on hub_plate() slot
    color("DimGray")
        base_bracket();

    // Articulated Upper Link pivoted at the MG996R shaft / 688ZZ bearing axis
    translate([12.0 + mg996r_shaft_off, 0, mg996r_d + 4.0 + 1.5])
        rotate([0, -shoulder_ang, 0]) {
            color("LightSteelBlue")
                upper_link();

            // Elbow Joint Bracket bolted to distal end of upper_link()
            translate([L_upper, 0, plate_thick]) {
                color("DimGray")
                    elbow_bracket();

                // Articulated Lower Link pivoted at MG90S elbow shaft
                translate([0, 0, mg90s_d + 7.5])
                    rotate([0, -elbow_ang, 0])
                        color("Silver")
                            lower_link();
            }
        }
}

module full_24_limb_assembly() {
    // 1. Central 260 mm rigid hub chassis
    color("DarkGray")
        hub_plate();

    // 2. 24 radial modular two-joint limbs at 15-degree increments
    for (i = [0 : num_limbs - 1]) {
        ang    = i * (360 / num_limbs);
        wave_s = pose_shoulder_deg + pose_wave_amp_deg * sin(ang * 3);
        wave_e = pose_elbow_deg    + pose_wave_amp_deg * 0.8 * cos(ang * 3);

        rotate([0, 0, ang])
            translate([hub_slot_r, 0, hub_thick])
                single_limb_assembled(wave_s, wave_e);
    }

    // 3. Central 3-Axis Camera Eye Gimbal mounted on top of reinforced hub boss
    translate([0, 0, hub_thick + 4.0])
        eye_gimbal(gimbal_pan_deg, gimbal_tilt_deg, gimbal_roll_deg);
}


// ============================================================================
// FABRICATION PRINT-PLATE LAYOUT (1 Complete Limb Set Flat on Z = 0)
// ============================================================================
module print_plate_single_limb() {
    translate([-60, -22, 0]) upper_link();
    translate([-50,  16, 0]) lower_link();
    translate([-35,  55, hub_thick - 0.5]) base_bracket();
    translate([ 35,  55, 0]) elbow_bracket();
}


// ============================================================================
// TOP-LEVEL 1-CLICK EXPORT DISPATCHER
// ============================================================================
if (export_part == "assembly") {
    full_24_limb_assembly();
} else if (export_part == "upper_link") {
    upper_link();
} else if (export_part == "lower_link") {
    lower_link();
} else if (export_part == "base_bracket") {
    base_bracket();
} else if (export_part == "elbow_bracket") {
    elbow_bracket();
} else if (export_part == "hub_plate") {
    hub_plate();
} else if (export_part == "eye_gimbal") {
    eye_gimbal();
} else if (export_part == "gimbal_pan_base") {
    gimbal_pan_base();
} else if (export_part == "gimbal_tilt_clevis") {
    gimbal_tilt_clevis();
} else if (export_part == "gimbal_roll_clevis") {
    gimbal_roll_clevis();
} else if (export_part == "gimbal_camera_cradle") {
    translate([0, 0, usb_collar_len])
        gimbal_camera_cradle();
} else if (export_part == "print_plate_single_limb") {
    print_plate_single_limb();
}
