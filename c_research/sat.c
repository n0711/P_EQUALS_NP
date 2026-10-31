/* C17 exact SAT baseline: deterministic DPLL with unit propagation. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef struct {int *a; int n;} Clause;
typedef struct {Clause *c; int m,n;} Formula;
typedef struct {uint64_t calls,branches,units;} Metrics;
static void die(const char *s){fprintf(stderr,"error: %s\n",s);exit(2);}
static Formula read_dimacs(FILE *fp){
 Formula f={0}; char line[4096]; int n=-1,m=-1,idx=0,cap=0,len=0,*tmp=NULL;
 while(fgets(line,sizeof line,fp)){
  if(line[0]=='c'||line[0]=='\n'||line[0]=='\r')continue;
  if(line[0]=='p') { if(sscanf(line,"p cnf %d %d",&n,&m)!=2||n<0||m<0)die("bad header"); f.n=n;f.m=m;f.c=calloc((size_t)m+1,sizeof *f.c);if(!f.c)die("oom");continue; }
  if(n<0)die("missing header");
  char *p=line,*end;
  while(1){long v=strtol(p,&end,10);if(end==p)break;p=end;
   if(v==0){if(idx>=m)die("too many clauses");f.c[idx].a=malloc((size_t)(len+1)*sizeof(int));if(!f.c[idx].a)die("oom");memcpy(f.c[idx].a,tmp,(size_t)len*sizeof(int));f.c[idx].n=len;idx++;len=0;}
   else {if(v>n||v< -n)die("literal exceeds variables");if(len==cap){cap=cap?cap*2:8;tmp=realloc(tmp,(size_t)cap*sizeof(int));if(!tmp)die("oom");}tmp[len++]=(int)v;}
  }
 }
 free(tmp);if(n<0||idx!=m||len)die("incomplete DIMACS");return f;
}
static int assign(int8_t *a,int lit){int v=abs(lit),val=lit>0?1:-1;if(a[v]&&a[v]!=val)return 0;a[v]=val;return 1;}
static int solve(const Formula *f,int8_t *a,Metrics *t){
 t->calls++;
 for(;;){int changed=0,unsat=0;
  for(int i=0;i<f->m;i++){Clause c=f->c[i];int freecount=0,last=0,satisfied=0;
   for(int j=0;j<c.n;j++){int l=c.a[j];int x=a[abs(l)];if(x==0){freecount++;last=l;}else if((x>0)==(l>0)){satisfied=1;break;}}
   if(satisfied)continue;
   if(!freecount){unsat=1;break;}
   if(freecount==1){if(!assign(a,last))return 0;t->units++;changed=1;break;}
  }
  if(unsat)return 0;
  if(!changed)break;
 }
 int pivot=0,remaining=0;
 for(int i=0;i<f->m;i++){Clause c=f->c[i];int satisfied=0;
  for(int j=0;j<c.n;j++){int l=c.a[j],x=a[abs(l)];if(x && ((x>0)==(l>0))){satisfied=1;break;}}
  if(satisfied)continue;
  remaining++;
  for(int j=0;j<c.n;j++)if(!a[abs(c.a[j])]){if(!pivot)pivot=abs(c.a[j]);break;}
 }
 if(!remaining)return 1;
 if(!pivot) return 0;
 int8_t *copy=malloc((size_t)f->n+1);if(!copy)die("oom");
 for(int val=1;val>=-1;val-=2){t->branches++;memcpy(copy,a,(size_t)f->n+1);copy[pivot]=(int8_t)val;
  if(solve(f,copy,t)){memcpy(a,copy,(size_t)f->n+1);free(copy);return 1;}}
 free(copy);return 0;
}
int main(int argc,char **argv){if(argc!=2)die("usage: sat_solver input.cnf");FILE *p=fopen(argv[1],"r");if(!p)die("cannot open file");Formula f=read_dimacs(p);fclose(p);int8_t *a=calloc((size_t)f.n+1,1);if(!a)die("oom");Metrics t={0};clock_t start=clock();int sat=solve(&f,a,&t);double sec=(double)(clock()-start)/CLOCKS_PER_SEC;
 if(sat){for(int i=0;i<f.m;i++){int ok=0;for(int j=0;j<f.c[i].n;j++){int l=f.c[i].a[j],v=a[abs(l)];if(v&&((v>0)==(l>0))){ok=1;break;}}if(!ok)die("invalid SAT witness");}}
 printf("{\"sat\":%s,\"calls\":%llu,\"branches\":%llu,\"units\":%llu,\"cpu_seconds\":%.9f}\n",sat?"true":"false",(unsigned long long)t.calls,(unsigned long long)t.branches,(unsigned long long)t.units,sec);
 free(a);for(int i=0;i<f.m;i++)free(f.c[i].a);free(f.c);return 0;}