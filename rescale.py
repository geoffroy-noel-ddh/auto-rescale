from subprocess import check_output, CalledProcessError, STDOUT
import re, os

#xrandr --output HDMI1 --scale 2x2 --mode 1920x1200 --fb 3840x4200 --pos 0x0
#xrandr --output eDP1 --scale 1x1 --pos 320x2400

class Rescaler(object):
    
    filepath = os.path.expanduser('~/.rescale.json')

    def rescale(self, options=None):
        self.options = options or []

        self.getDisplaySettings()

        self.showDisplaySettings()

        if 'show' in options:
            return
        
        if 'save' in options:
            self.saveDisplaySettings()

        if 'load' in options:
            self.loadDisplaySettings()

        if 'auto' in options:
            self.updateDisplaySettings()
    
        if 'auto' in options or 'load' in options or 'reset' in options :
            self.showDisplaySettings()
    
            self.applyDisplaySettings()

    def saveDisplaySettings(self):
        import json
        f = open(self.filepath, 'wb')
        f.write(json.dumps(self.settings))
        f.close()

    def loadDisplaySettings(self):
        import json
        f = open(self.filepath, 'rt')
        self.settings = json.loads(f.read())
        f.close()

    def showDisplaySettings(self):
        print '-' * 40
        for s in self.settings:
            s['sx'] = 1.0 * s['wspx'] / s['wpx']
            s['sy'] = 1.0 * s['hspx'] / s['hpx']
            print '%(output)s res:%(wpx)sx%(hpx)s pos:%(oxpx)sx%(oypx)s scale:%(sx).1fx%(sy).1f dim:%(wmm)sx%(hmm)s' % s
        print '-' * 40

    def getDisplaySettings(self):
        # $ xrandr -q --verbose
        # HDMI2 connected 2880x1620+0+0 (0x4a) normal (normal left inverted right x axis y axis) 510mm x 290mm
        # 1920x1080 (0x4a) 148.500MHz +HSync +VSync *current +preferred

        settings = []

        info = self.run('xrandr -q --verbose')

        for line in info['output'].split('\n'):
            parts = re.findall(ur'^([\w-]+) connected (\d+)x(\d+)\+(\d+)\+(\d+)\s.+\s(\d+)mm.*?(\d+)mm', line)
            if parts:
                parts = parts[0]
                settings.append({
                    'output': parts[0],
                    'wspx': int(parts[1]),
                    'hspx': int(parts[2]),
                    'oxpx': int(parts[3]),
                    'oypx': int(parts[4]),
                    'wmm': int(parts[5]),
                    'hmm': int(parts[6]),
                })

            parts = re.findall(ur'(\d+)x(\d+)\s.*\s*current', line)
            if parts and settings:
                parts = parts[0]
                s = settings[-1]
                s.update({
                    'wpx': int(parts[0]),
                    'hpx': int(parts[1]),
                })


        self.settings = settings

    def updateDisplaySettings(self):
        #new_settings = []

        # get the reference display, the one that is never rescaled
        ref = None
        for s in self.settings:
            if s['output'] in ['eDP1']:
                ref = s

        if ref:
            # rescale the other displays to match the the reference
            # the objective is that the same size in pixel
            # will appear the same size visually.
            # IMPORTANT ASSUMPTION: displays are side by side.
            for s in self.settings:
                if s['output'] != ref['output']:
                    s['sx'] = (1.0 * s['wmm'] / ref['wmm']) * (1.0 * ref['wpx'] / s['wpx'])
                    s['sy'] = (1.0 * s['hmm'] / ref['hmm']) * (1.0 * ref['hpx'] / s['hpx'])
                else:
                    s['sx'] = 1.0
                    s['sy'] = 1.0
                #print s['sx'], s['sy']

                # round the scaling to first decimal
                for f in ['sx', 'sy']:
                    s[f] = round(s[f], 1)

                # experimental: take the smallest scale factor
                # apply it to both dimensions
                if 1:
                    s['sy'] = min(s['sx'], s['sy'])
                    s['sy'] = min(2,s['sy'])
                    s['sx'] = s['sy']

                # align to nearest half unit
                granularity = 0.25
                if 1:
                    for f in ['sx', 'sy']:
                        s[f] = int(s[f]/granularity)*granularity

                if 'reset' in self.options:
                    for f in ['sx', 'sy']:
                        s[f] = 1

                # recalculate the scaled width and height
                s['wspx'] = int(s['sx'] * s['wpx'])
                s['hspx'] = int(s['sy'] * s['hpx'])

            # recalculate the position of each display on the virtual space
            pos = [0, 0]
            for s in sorted(self.settings, key=lambda s: s['oxpx']):
                # place them side by side without gap
                s['oxpx'] = pos[0]
                pos[0] += s['wspx']

                # align each display with the bottom line
                s['oypx'] = max([s2['hspx'] for s2 in self.settings]) - s['hspx']

        #self.settings = new_settings

    def applyDisplaySettings(self):
        if self.settings:
            fb = [
                sum([s2['wspx'] for s2 in self.settings]),
                max([s2['hspx'] for s2 in self.settings])
            ]
            command = 'xrandr --fb %dx%d' % (fb[0], fb[1])
            for s in self.settings:
                # scaling
                command += ' '
                s['sx'] = 1.0 * s['wspx'] / s['wpx']
                s['sy'] = 1.0 * s['hspx'] / s['hpx']
                s['wfb'] = fb[0]
                s['hfb'] = fb[1]
                # frame buffer size for the entire virtual screen
                s['scale'] = ' --scale %(sx).2fx%(sy).2f ' % s
                if '--noscale' in self.options:
                    s['scale'] = ''
                command += '--output %(output)s --mode %(wpx)dx%(hpx)d %(scale)s --panning 0x0+0+0/0x0+0+0/0/0/0/0 --pos %(oxpx)dx%(oypx)d ' % s
            print command
            if not '--dry-run' in self.options:
                r = self.run(command)
                print r['output']
            command = 'xrandr --fb %dx%d' % (fb[0], fb[1])
            
            for s in self.settings:
                command += ' '
                command += '--output %(output)s --panning %(wspx)sx%(hspx)s+%(oxpx)s+%(oypx)s/%(wspx)sx%(hspx)s+%(oxpx)s+%(oypx)s/0/0/0/0' % s
            print command
            if not '--dry-run' in self.options and not '--nopanning' in self.options:
                r = self.run(command)
                print r['output']
        # xrandr --output eDP1 --scale 1.0x1.0 --mode 1920x1080 --fb 4800x1620 --pos 1920x0
        # xrandr --output HDMI2 --scale 1.5x1.5 --mode 1920x1080 --fb 4800x1620 --pos 0x0


    def run(self, command):
        ret = {'output': None, 'error': 0}
        try:
            output = check_output(command, stderr=STDOUT, shell=True, universal_newlines=True)
        except CalledProcessError as exc:
            ret = {'error': exc.returncode, 'output': exc.output}
            print exc.output
            raise exc
        else:
            ret['output'] = output
        return ret

#-------------------------

import sys

rescaler = Rescaler()
rescaler.rescale(sys.argv[1:])

# ret = run('xrandr -q')
# print ret

print 'done'
