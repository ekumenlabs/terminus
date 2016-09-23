from city_model import CityModel

class Block(CityModel):
    def __init__(self, origin):
        super(Block, self).__init__()
        self.origin = origin

    def template(self):
        return """
          <model name="{{model.name}}">
             <static>1</static>
             <allow_auto_disable>1</allow_auto_disable>
             <link name="{{model.name}}_link">
                <pose frame="">{{model.origin.x}} {{model.origin.y}} {{model.origin.z}} 0 0 0</pose>
                <collision name="{{model.name}}_collision">
                   <geometry>
                      <box>
                         <size>95 95 0.15</size>
                      </box>
                   </geometry>
                </collision>
                <visual name="{{model.name}}_visual">
        <cast_shadows>1</cast_shadows>
        <transparency>0</transparency>
        <material>
          <shader type='vertex'>
            <normal_map>__default__</normal_map>
          </shader>
          <lighting>0</lighting>
        </material>
                   <meta>
                      <layer>0</layer>
                   </meta>
                   <geometry>
                      <box>
                         <size>95 95 0.15</size>
                      </box>
                   </geometry>
                </visual>
             </link>
          </model>"""

