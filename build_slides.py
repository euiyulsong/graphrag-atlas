"""The revised presentation is bundled as an editable PPTX."""
from pathlib import Path
if __name__ == '__main__':
    print(Path(__file__).parent / 'slides' / 'GraphRAG_Atlas_Tech_Seminar.pptx')
    print('The revised deck is prebuilt. Edit it in PowerPoint; this script does not regenerate legacy slides.')
