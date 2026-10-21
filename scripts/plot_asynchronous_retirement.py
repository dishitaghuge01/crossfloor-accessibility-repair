"""Vector explanatory figure; semantic trace, not measured benchmark data."""
import argparse
from pathlib import Path


def build(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
    fig,ax=plt.subplots(figsize=(7.1,2.9))
    labels=['Buy a','Project x0','Buy b','Close U','Test Q','Close V']
    rows=[('Profile 0 vertex x0',[1,0,0,0,0,0],'#3478b7'),
          ('Owner identity O',[1,1,1,0,0,0],'#db9730'),
          ('Paid occupancy at c',[1,1,1,1,1,0],'#8a5ca5')]
    for i,(label,values,color) in enumerate(rows):
        y=2-i
        ax.text(-.7,y+.35,label,ha='right',va='center')
        for x,present in enumerate(values):
            ax.add_patch(Rectangle((x,y),.85,.7,facecolor=color if present else '#eeeeee',edgecolor='white'))
            ax.text(x+.425,y+.35,'retained' if present else 'erased',ha='center',va='center',fontsize=7,
                    color='white' if present else '#555555')
    ax.annotate('Same-owner reuse remains valid',xy=(2.4,1.7),xytext=(2.4,3.15),ha='center',fontsize=8,
                arrowprops={'arrowstyle':'->','color':'#555555'})
    ax.annotate('Competing Q rejected',xy=(4.4,.7),xytext=(4.3,-.8),ha='center',fontsize=8,
                arrowprops={'arrowstyle':'->','color':'#555555'})
    ax.set_xticks([x+.425 for x in range(6)],labels)
    ax.tick_params(axis='x',length=0)
    ax.set_xlim(-.5,6);ax.set_ylim(-.2,3.5);ax.set_yticks([])
    for spine in ax.spines.values():spine.set_visible(False)
    fig.subplots_adjust(left=.27,right=.99,bottom=.28,top=.97)
    fig.savefig(output/'asynchronous-retirement.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(output/'asynchronous-retirement.png',dpi=200)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    build(p.parse_args().output)
