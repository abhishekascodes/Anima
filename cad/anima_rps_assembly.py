"""ANIMA upper torso R1. All dimensions are in millimetres.

Run with CadQuery 2.6 on Python 3.11. The assembly's front is positive Y.
Supplier envelopes are references. Verify hole patterns and clearances against purchased parts.
"""
from pathlib import Path
import json
import math
import sys

HERE = Path(__file__).resolve().parent
if (HERE / 'pydeps').is_dir():
    sys.path.insert(0, str(HERE / 'pydeps'))
import cadquery as cq

BUILD = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE / 'anima-rps-mechanical'
PARTS = BUILD / 'parts'
PARTS.mkdir(parents=True,exist_ok=True)
palette = {'ivory':(.79,.68,.48),'frame':(.045,.058,.071),'metal':(.16,.20,.22),
           'orange':(.78,.28,.075),'visor':(.012,.021,.027),'light':(.92,.39,.10),
           'green':(.06,.26,.20),'glass':(.50,.72,.73),'steel':(.34,.38,.40),'rubber':(.026,.029,.031),
           'stop_red':(.65,.027,.028)}
library = {}
catalog = {}
instances = []
rig = cq.Assembly(name='ANIMA_RPS_Upper_Torso_R1')


def box(dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz).val()


def panel(points,thickness,axis='XZ'):
    part = cq.Workplane(axis).polyline(points).close().extrude(thickness).val()
    return part.translate((0,thickness/2,0)) if axis=='XZ' else part


def cyl(radius,length,origin=(0,0,0),direction=(0,0,1)):
    return cq.Solid.makeCylinder(radius,length,cq.Vector(*origin),cq.Vector(*direction))


def drilled(part,rows,direction=(0,0,1)):
    for x,y,z,r in rows:
        part = part.cut(cyl(r,20,(x,y,z),direction))
    return part


def shaped_tube(points,radius):
    segments=[]
    for a,b in zip(points,points[1:]):
        delta=cq.Vector(*b)-cq.Vector(*a)
        segments.append(cyl(radius,delta.Length,a,delta.toTuple()))
    return cq.Compound.makeCompound(segments)


def register(name,part,mat,reason='Modelled component',reference=False):
    if not part.isValid() or part.Volume() <= 0:
        raise ValueError(f'Invalid solid {name}')
    library[name]=(part,mat)
    catalog[name]={'classification':'Envelope' if reference else 'Modelled part','description':reason}
    if not reference:
        cq.exporters.export(part,str(PARTS/(name+'.step')))


def fit(key,pos=(0,0,0),y_angle=0,z_angle=0,label=None,x_angle=0):
    solid,mat=library[key]
    name=label or key
    transformed=solid.rotate((0,0,0),(0,1,0),y_angle).rotate((0,0,0),(1,0,0),x_angle).rotate((0,0,0),(0,0,1),z_angle).translate(pos)
    rig.add(transformed,name=name,color=cq.Color(*palette[mat]))
    instances.append((name,mat,transformed))


def paired(key,a,b,labels):
    fit(key,a,label=labels[0]); fit(key,b,label=labels[1])


base_holes=[(x,y,-8,3.25) for x in (-180,180) for y in (-158,158)]
base_holes.extend((x,y,-8,2.65) for x in (-39,39) for y in (-52,-12))
base_holes.extend((86+x,-63+y,-8,1.6) for x in (-66,65) for y in (-45.5,45.5))
base_holes.extend((-127+x,45+y,-8,1.45) for x in (-39,19) for y in (-24.5,24.5))
register('base_plate',drilled(box(420,380,6),base_holes),'metal','420 x 380 x 6 blank, hole pattern is provisional')
fit('base_plate',(0,0,8))
deck_mounts=[(x,y,-8,2.15) for x in (-185,185) for y in(-165,165)]
deck_mounts.extend([(94,120,-8,1.65),(154,120,-8,1.65),(124,120,-8,4)])
register('service_top_deck',drilled(box(406,365,4),deck_mounts),'frame')
fit('service_top_deck',(0,0,43))
estop_pod=box(62,60,49).cut(box(52,50,48).translate((0,0,-5))).cut(cyl(11.1,10,(0,0,17)))
register('estop_pod',estop_pod,'frame','Low-voltage stop enclosure with provisional 22 mm operator hole; verify depth and fasteners.')
fit('estop_pod',(124,120,69.5))
register('estop_mount_tab',drilled(box(16,14,4),[(0,0,-5,1.65)]),'steel')
paired('estop_mount_tab',(94,120,47),(154,120,47),('estop_left_tab','estop_right_tab'))
register('estop_operator_envelope',cyl(20,9),'stop_red','Representative latching mushroom operator. Confirm selected body and contact depth.',True)
fit('estop_operator_envelope',(124,120,94))
register('base_side_panel',box(4,365,29),'frame')
paired('base_side_panel',(-201,0,26),(201,0,26),('service_left','service_right'))
fascia=panel([(-195,-13),(195,-13),(202,0),(195,13),(-195,13),(-202,0)],4)
register('status_fascia',fascia,'metal')
fit('status_fascia',(0,-182,26),label='back_fascia')
front_fascia=fascia.cut(cyl(3,8,(0,-4,-1),(0,1,0)))
for x in (-46,46):
    front_fascia=front_fascia.cut(cyl(8,8,(x,-4,-1),(0,1,0)))
register('front_control_fascia',front_fascia,'metal','Provisional 6 mm toggle bushing and 16 mm pushbutton cutouts. Fit actual panel parts.')
fit('front_control_fascia',(0,182,26),label='front_fascia')
register('rubber_foot',cyl(14,5),'rubber','Rubber foot reference',True)
for i,(x,y) in enumerate([(-180,-158), (180,-158),(180,158),(-180,158)],1):
    fit('rubber_foot',(x,y,0),label=f'foot_{i}')

register('spine_rail',box(20,40,348),'metal','Two 20 x 40 rectangular structural rail envelopes')
paired('spine_rail',(-39,-32,218),(39,-32,218),('spine_left','spine_right'))
register('spine_crossmember',box(150,24,16),'metal')
for i,z in enumerate((75,217,355),1): fit('spine_crossmember',(0,-31,z),label=f'spine_cross_{i}')
register('rear_cover',panel([(-65,5),(65,5),(85,255),(64,330),(-64,330),(-85,255)],3),'frame')
fit('rear_cover',(0,-62,46))
register('backbone_cover',panel([(-62,2),(62,2),(81,174),(93,290),(63,337),(-63,337),(-93,290),(-81,174)],8),'frame')
fit('backbone_cover',(0,11,49))

front = panel([(-79,-115),(78,-115),(106,62),(75,109),(-68,109),(-105,65)],5)
front = front.cut(box(123,14,43).translate((0,0,33)))
for z in (-24,-30,-36,-42):
    front = front.cut(box(33,15,2.4).translate((0,0,z)))
register('chest_front_shell',front,'ivory','Cut from flat stock. Includes the display opening and four speaker slots.')
fit('chest_front_shell',(0,43,259))
register('speaker_envelope',box(40,20,38),'frame','Provisional 4 ohm enclosed speaker envelope behind the chest slots.',True)
fit('speaker_envelope',(0,29,227))
register('display_bezel',box(132,8,52).cut(box(118,20,39)),'metal')
fit('display_bezel',(0,50,292))
register('display_panel_envelope',box(118,5,39),'visor','Replace with exact 8 x 32 module dimensions',True)
fit('display_panel_envelope',(0,47,292))
for n,x in enumerate((-39,0,39),1):
    shape=box(19,1.8,2.1)
    for j,i in enumerate((0,3.7,7.4),1):
        ref=f'display_bar_{n}_{j}'
        register(ref,shape,'light','Illustrative LEDs in the chest module',True)
        fit(ref,(x,50.8,289+i))

shoulder = [(-188,-5),(-151,29),(-106,22),(-64,11),(-74,-31),(-157,-43),(-177,-22)]
register('playing_shoulder_shell',panel(shoulder,6),'ivory')
register('countdown_shoulder_shell',panel([(-x,z) for x,z in reversed(shoulder)],6),'ivory')
fit('playing_shoulder_shell',(0,39,378)); fit('countdown_shoulder_shell',(0,39,378))
register('shoulder_support',box(295,24,14),'metal')
fit('shoulder_support',(0,0,371))
register('neck_pedestal',drilled(box(76,58,8),[(a,b,-8,2.65) for a in (-27,27) for b in (-19,19)]),'metal')
fit('neck_pedestal',(0,-10,395))
register('neck_turntable',cyl(31,20),'metal')
fit('neck_turntable',(0,-10,399))
register('neck_tilt_cheek',panel([(-11,0),(10,0),(14,27),(7,42),(-8,42),(-14,27)],5)
    .cut(cyl(4.1,20,(0,-10,30),(0,1,0))),'steel')
fit('neck_tilt_cheek',(-44,-3,413),z_angle=90,label='tilt_cheek_left')
fit('neck_tilt_cheek',(44,-3,413),z_angle=90,label='tilt_cheek_right')
register('ds3225_envelope',box(42,22,43),'frame','Provisional DS3225 pan and countdown elbow volume.',True)
register('mg996r_envelope',box(42,21,44),'frame','Provisional MG996R head tilt volume.',True)
fit('ds3225_envelope',(0,-27,402),label='head_pan_servo')
fit('mg996r_envelope',(32,-4,460),y_angle=90,label='head_tilt_servo')

face=[(-81,16),(-51,57),(47,57),(79,24),(72,-35),(29,-53),(-28,-53),(-72,-34)]
inner_face=[(.85*x,.85*z) for x,z in face]
register('head_rear_shell',panel(face,38).cut(panel(inner_face,38).translate((0,5,0))),
         'frame','Hollow shell with open service side')
fit('head_rear_shell',(0,0,493))
register('head_face_plate',panel(face,6),'ivory')
fit('head_face_plate',(0,22,493))
register('smoked_visor',panel([(-67,23),(67,23),(53,-21),(-53,-21)],6),'visor')
fit('smoked_visor',(0,27,497))
register('eye_diffuser',panel([(-13,2),(13,2),(11,-2.4),(-11,-2.4)],1.8),'light')
paired('eye_diffuser',(-30,31,500),(30,31,500),('eye_left','eye_right'))
register('jaw_shell',panel([(-25,5),(25,5),(20,-6),(-20,-6)],10),'metal')
fit('jaw_shell',(0,29,455))
register('microservo_envelope',box(24,13,25),'frame','Provisional MG90S volume',True)
fit('microservo_envelope',(0,0,457),label='jaw_servo')

register('fixed_camera_arm',box(12,48,56),'metal')
fit('fixed_camera_arm',(132,26,402))
register('camera_mount_plate',drilled(box(56,6,40),[(x,-9,z,1.50) for x in(-17,17) for z in(-12,12)],(0,1,0)),'metal')
register('camera_board_envelope',box(25,2,24),'green','Camera Module 3 envelope. Verify the throw-zone crop with actual optics.',True)
register('camera_lens_envelope',cyl(5.2,8,(0,0,0),(0,1,0)),'visor','Camera lens envelope',True)
register('camera_shutter_blade',panel([(-9,12),(17,12),(23,5),(23,-8),(-9,-12),(-15,-4),(-15,5)],2)
    .cut(cyl(1.6,20,(-8,-10,5),(0,1,0))),'orange')


def aim_camera(name, local, clock=0, label=None):
    pitch, yaw = -60, 26
    p, y=math.radians(pitch),math.radians(yaw)
    lx,ly,lz=local
    dy=ly*math.cos(p)-lz*math.sin(p)
    dz=ly*math.sin(p)+lz*math.cos(p)
    offset=(lx*math.cos(y)-dy*math.sin(y),lx*math.sin(y)+dy*math.cos(y),dz)
    pivot=(132,55,427)
    fit(name,tuple(a+b for a,b in zip(pivot,offset)),clock,yaw,label,x_angle=pitch)


aim_camera('camera_mount_plate',(0,0,0))
aim_camera('camera_board_envelope',(-3,4,0))
aim_camera('camera_lens_envelope',(-3,6,0))
aim_camera('camera_shutter_blade',(18,14,10),clock=-32)
aim_camera('microservo_envelope',(21,-7,3),label='shutter_servo')

register('countdown_upper_link',panel([(-15,7),(15,7),(22,-98),(14,-117),(-14,-117),(-22,-99)],19),'metal')
fit('countdown_upper_link',(147,29,353),y_angle=-9)
fit('ds3225_envelope',(147,13,234),y_angle=90,label='elbow_servo')
register('countdown_forearm_shell',panel([(-20,4),(20,4),(26,-73),(15,-94),(-15,-94),(-25,-72)],20),'ivory')
fit('countdown_forearm_shell',(154,42,236),y_angle=-18)
register('countdown_striker_pad',box(35,38,14),'rubber')
fit('countdown_striker_pad',(179,48,151),y_angle=-18)
register('strike_plate_post',box(17,23,83),'metal')
fit('strike_plate_post',(179,45,88))
register('strike_plate',box(42,50,8),'orange')
fit('strike_plate',(179,45,132))

register('right_arm_support',box(20,28,165),'metal')
fit('right_arm_support',(-130,71,126))
register('right_forearm_shell',panel([(-23,44),(14,51),(29,34),(27,-36),(9,-47),(-22,-37)],32),'metal')
fit('right_forearm_shell',(-137,61,234),y_angle=11)
register('wrist_bracket',drilled(box(69,30,8),[(x,y,-8,1.65) for x in(-27,27) for y in(-8,8)]),'steel')
fit('wrist_bracket',(-131,91,174))
register('playing_palm',panel([(-40,-23),(-33,27),(30,29),(40,10),(32,-28),(-20,-33)],17),'frame')
fit('playing_palm',(-127,103,152))

def finger_link(name,length,width):
    link=panel([(-width/2,4),(width/2,4),(width/2,-length+6),
                (width/2-3,-length),(-width/2+3,-length),(-width/2,-length+6)],8)
    link=drilled(link,[(0,-10,-1,1.55),(0,-10,-length+4.5,1.55)],(0,1,0))
    link=link.cut(cyl(1.15,20,(2.5,-10,-10),(0,1,0)))
    register(name,link,'ivory','Tendon and two pivot interfaces. Bore compensation required on print test.')


for name,length,width in [('long_finger_base',36,12),('short_finger_base',29,12),('finger_tip',25,11),('thumb_base',26,13)]:
    finger_link(name,length,width)
for i,(x,z,length,alpha) in enumerate([(-149,136,36,3),(-134,135,36,-3),(-119,135,29,-14),(-104,136,29,-25)],1):
    fit('long_finger_base' if i<3 else 'short_finger_base',(x,113,z),y_angle=alpha,label=f'finger_{i}_base')
    # Display pose illustration. Orient the tips towards the palm for two curled fingers.
    fit('finger_tip',(x+ (1 if i<3 else 8),113,z-length+5),y_angle=alpha if i<3 else -82,label=f'finger_{i}_tip')
fit('thumb_base',(-162,111,158),y_angle=49,label='thumb_base')
fit('finger_tip',(-178,111,143),y_angle=86,label='thumb_tip')
register('tendon_guide',box(67,15,10),'steel')
fit('tendon_guide',(-128,94,204))
register('solenoid_envelope',box(38,21,20),'metal','Oversize JF-0730B-class envelope, check actual SKU',True)
for i,x in enumerate((-161,-124,-87),1):
    fit('solenoid_envelope',(x,69,143),z_angle=90,label=f'coil_{i}')
    guide=f'tendon_route_{i}'
    register(guide,shaped_tube([(x,77,146),(x,83,176),(x,92,200),(x,102,165)],.78),'orange','Tendon routing study',True)
    fit(guide)
register('guard_sheet',box(152,3,146),'glass','Front guard envelope. Check hand sweep and opening with hardware.')
fit('guard_sheet',(-126,141,121))
register('guard_side',box(3,79,146),'glass')
paired('guard_side',(-203,102,121),(-49,102,121),('guard_left_return','guard_right_return'))
register('guard_bottom_rail',box(152,12,8),'steel')
fit('guard_bottom_rail',(-126,141,49))

register('controller_board_envelope',drilled(box(140,99,1.6),[(x,y,-6,1.6) for x in(-66,65) for y in(-45.5,45.5)]),'green','PCB reference envelope from the native KiCad design',True)
fit('controller_board_envelope',(86,-63,19))
register('logic_connectors_envelope',box(130,9,12),'frame','Reserve connector and cable space in base',True)
fit('logic_connectors_envelope',(86,-110,26))
register('mini_power_envelope',box(111,62,28),'metal','DC distribution and regulator volume only. Size mains supply separately.',True)
fit('mini_power_envelope',(-129,-76,26))
register('pi5_board_envelope',drilled(box(85,56,1.6),[(x,y,-4,1.4) for x in(-39,19) for y in(-24.5,24.5)]),'green','Pi 5 8 GB board outline with provisional standoff placement.',True)
fit('pi5_board_envelope',(-127,45,15))
register('pi5_port_envelope',box(17,51,16),'steel','USB and Ethernet volume. Keep the negative X service approach free.',True)
fit('pi5_port_envelope',(-159,45,24))
register('pi5_cooler_envelope',box(55,39,12),'metal','Reserve volume for Raspberry Pi Active Cooler.',True)
fit('pi5_cooler_envelope',(-122,45,23))
register('pi5_nvme_hat_envelope',box(65,56,2),'green','M.2 HAT+ and 256 GB NVMe assembly reference. Check underside clearances and airflow.',True)
fit('pi5_nvme_hat_envelope',(-121,45,32))
register('pi5_nvme_envelope',box(30,22,4),'steel','Raspberry Pi 256 GB M.2 SSD reference.',True)
fit('pi5_nvme_envelope',(-118,45,35))
toggle=cyl(7,2,(0,0,0),(0,1,0)).fuse(cyl(2.8,10,(0,2,0),(0,1,0)))
register('toggle_envelope',toggle,'steel','Metal mode switch reference',True)
# Place both control families so their modeled caps end at the base edge, Y=190.
fit('toggle_envelope',(0,178,25))
button=cyl(7.9,4,(0,0,0),(0,1,0)).fuse(cyl(10,6,(0,4,0),(0,1,0)))
register('arcade_button_envelope',button,'orange','Buttons on external fascia',True)
paired('arcade_button_envelope',(-46,180,25),(46,180,25),('start_button','rematch_button'))

rig.save(str(BUILD/'ANIMA_RPS_Upper_Torso.step'),exportType='STEP')
meshes=[]
for name,mat,shape in instances:
    verts,faces=shape.tessellate(.40)
    meshes.append({'name':name,'material':mat,'points':[v.toTuple() for v in verts],'faces':faces})
(BUILD/'render_scene.json').write_text(json.dumps({'materials':palette,'meshes':meshes},separators=(',',':')),encoding='utf-8')
(BUILD/'part_index.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
print(f'{len(instances)} assembly instances, {len(list(PARTS.glob("*.step")))} individual part STEP files')
